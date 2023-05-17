import {
  Type,
  EntryBase,
  EntryTask,
  Entry,
  StatusLevel,
  EntryMethod,
  Argument,
} from '../lib/types';
import { setAllEntriesWhenPossible, setRunInfoWhenPossible } from './effectCallbacks';
import { Decoder, iter_decoded_log_format, IMessage } from './decoder';
import { IOpts, PythonTraceback } from './protocols';
import { getIntLevelFromStatus } from './status';
import { Counter, RunInfo, RunInfoStatus, logError } from '../lib';

/**
 * Helpers to make sure that we only have 1 active tree builder.
 * Whenever we enter a tree builder async-related function it must
 * be checked.
 */
let globalLeaseId = 0;
let globalCurrentLease = -1;
function obtainNewLease() {
  globalLeaseId += 1;
  globalCurrentLease = globalLeaseId;
  return globalLeaseId;
}

class TBHandler {
  private stack: PythonTraceback[] = [];

  /**
   * @returns undefined if the traceback is being built, otherwise if the
   * traceback is fully built the PythonTraceback is provided.
   */
  handle(msg: IMessage): PythonTraceback | undefined {
    let tb: PythonTraceback | undefined;
    switch (msg.message_type) {
      case 'STB': // start
        this.stack.push(new PythonTraceback(msg.decoded.message));
        return undefined;

      case 'TBE': // tb entry
        tb = this.stack.at(-1);
        if (tb === undefined) {
          console.log('Unable to pop stack entry because the stack is empty.');
          return undefined;
        }
        tb.pushEntry(
          msg.decoded.source,
          msg.decoded.lineno,
          msg.decoded.method,
          msg.decoded.line_content,
        );
        return undefined;

      case 'TBV': // variable
        // We no longer push variabes into the stack because we're not using them
        // right now (as we record assigns as they happen in a scope).
        // tb = this.stack.at(-1);
        // tb.pushVar(msg.decoded["name"], msg.decoded["type"], msg.decoded["value"]);
        return undefined;

      case 'ETB': // tb end
        tb = this.stack.pop();
        if (tb === undefined) {
          console.log('Unable to pop stack entry because the stack is empty.');
          return undefined;
        }
        tb.stack.reverse();
        return tb;
    }
  }
}

class FlattenedTree {
  public entries: Entry[] = [];

  public stack: Entry[] = [];
  public stackCounter: Counter[] = [new Counter()];

  private argsTarget: EntryMethod | undefined;

  private parentId = '';

  newScopeId(): string {
    let counter = this.stackCounter.at(-1);
    if (counter === undefined) {
      throw new Error('Error stack counter must always have at least 1 entry.');
    }
    const newId =
      this.parentId.length === 0 ? `root${counter.next()}` : `${this.parentId}-${counter.next()}`;
    this.parentId = newId;

    this.stackCounter.push(new Counter());

    return newId;
  }

  pushMethodScope(msg: IMessage) {
    // console.log('pushMethodScope');
    let name = msg.decoded['name'];
    if (msg.message_type == 'YR') {
      name += ' (resumed)';
    }

    const entry: EntryMethod = {
      id: this.newScopeId(),
      type: Type.method,
      name: msg.decoded.name,
      libname: msg.decoded.libname,
      source: msg.decoded.source,
      lineno: msg.decoded.lineno,
      endDeltaInSeconds: -1,
      status: StatusLevel.unset,
      startDeltaInSeconds: msg.decoded.time_delta_in_seconds,
      entriesIndex: this.entries.length,
      arguments: undefined,
    };
    this.stack.push(entry);
    this.entries.push(entry);
    this.argsTarget = entry;
  }

  addArguments(msg: IMessage) {
    if (this.argsTarget !== undefined) {
      const targetCp: EntryMethod = <EntryMethod>{ ...this.argsTarget };
      const arg: Argument = {
        name: msg.decoded.name,
        type: msg.decoded.type,
        value: msg.decoded.value,
      };
      if (!targetCp.arguments || targetCp.arguments.length === 0) {
        targetCp.arguments = [arg];
      } else {
        targetCp.arguments = [...targetCp.arguments, arg];
      }

      // Update the references to the new object to avoid mutability.
      this.entries[targetCp.entriesIndex] = targetCp;
      this.argsTarget = targetCp;
      for (let index = this.stack.length - 1; index >= 0; index--) {
        const element = this.stack[index];
        if (element.entriesIndex === targetCp.entriesIndex) {
          this.stack[index] = targetCp;
          break;
        }
      }
    }
  }

  pushTaskScope(msg: IMessage) {
    // console.log('pushTaskScope');
    const entry: EntryTask = {
      id: this.newScopeId(),
      type: Type.task,
      name: msg.decoded.name,
      libname: msg.decoded.libname,
      source: msg.decoded.source,
      lineno: msg.decoded.lineno,
      endDeltaInSeconds: -1,
      status: StatusLevel.unset,
      startDeltaInSeconds: msg.decoded.time_delta_in_seconds,
      entriesIndex: this.entries.length,
    };
    this.stack.push(entry);
    this.entries.push(entry);
  }

  popScope(msg: IMessage, type: Type): EntryBase | undefined {
    let entry: EntryBase | undefined;
    while (true) {
      if (this.stack.length === 0) {
        console.log(
          `Unable to find scope start when receiving end message: ${JSON.stringify(msg)}.`,
        );
        return;
      }
      entry = this.stack.pop();
      if (this.stackCounter.length > 1) {
        // i.e.: the root entry must be always there (even if messages become wrong and we have
        // more endings than starts).
        this.stackCounter.pop();
      }
      if (entry?.type === type) {
        if (this.stack.length > 0) {
          const last = this.stack.at(-1);
          if (last === undefined) {
            throw new Error('Stack is not empty yet accessing last item returned undefined.');
          }
          this.parentId = last.id;
        } else {
          this.parentId = '';
        }
        break;
      }
    }
    return entry;
  }

  popMethodScope(msg: IMessage) {
    // Note: create a copy and assign it in the entries array (we don't want to mutate the
    // entry that's being used in react).
    const entry: EntryBase | undefined = this.popScope(msg, Type.method);
    if (entry === undefined) {
      return;
    }
    const methodScopeEntry: EntryMethod = <EntryMethod>{ ...entry };
    const { status } = msg.decoded;
    methodScopeEntry.status = getIntLevelFromStatus(status);
    methodScopeEntry.endDeltaInSeconds = msg.decoded.time_delta_in_seconds;

    this.entries[methodScopeEntry.entriesIndex] = methodScopeEntry;
  }

  popTaskScope(msg: IMessage) {
    const entry: EntryBase | undefined = this.popScope(msg, Type.task);
    if (entry === undefined) {
      return;
    }

    // Note: create a copy and assign it in the entries array (we don't want to mutate the
    // entry that's being used in react).
    const taskScopeEntry: EntryTask = <EntryTask>{ ...entry };
    const { status } = msg.decoded;
    taskScopeEntry.status = getIntLevelFromStatus(status);
    taskScopeEntry.endDeltaInSeconds = msg.decoded.time_delta_in_seconds;

    this.entries[taskScopeEntry.entriesIndex] = taskScopeEntry;
  }
}

/**
 * A helper class to build the tree.
 *
 * Note that as it adds nodes using async, care must be taken to
 * synchronize operations so that messages are handled in the proper
 * order.
 */
export class TreeBuilder {
  readonly opts: IOpts;

  // A unique incremental id.
  id = 0;

  readonly runId: string | undefined;

  finishedAddingInitialContents = false;

  lease: number;

  appendedMessagesIndex = -1;

  decoder: Decoder = new Decoder();

  seenSuiteTaskOrElement = false;

  tbHandler: TBHandler = new TBHandler();

  suiteErrored = false;

  flattened: FlattenedTree = new FlattenedTree();

  constructor(opts: IOpts) {
    this.opts = opts;
    this.runId = this.opts.runId;
    this.lease = obtainNewLease();
    this.resetState();
  }

  private runInfo: RunInfo = {
    description: 'Waiting for run to start ...',
    time: '',
    status: 'UNSET',
    finishTimeDeltaInSeconds: undefined,
  };

  private runInfoChanged: boolean = false;

  updateRunInfoName(name: string) {
    this.runInfo.description = name;
    this.runInfoChanged = true;
  }

  updateRunInfoTime(time: string) {
    this.runInfo.time = time;
    this.runInfoChanged = true;
  }

  updateRunInfoStatus(status: RunInfoStatus) {
    this.runInfo.status = status;
    this.runInfoChanged = true;
  }

  updateRunInfoFinishTime(timeDeltaInSeconds: number) {
    this.runInfo.finishTimeDeltaInSeconds = timeDeltaInSeconds;
    this.runInfoChanged = true;
  }

  resetState() {
    this.seenSuiteTaskOrElement = false;
  }

  /**
   * Should be used to know if this instance is the current one.
   */
  isCurrentTreeBuilder() {
    return this.lease === globalCurrentLease && this.runId == this.opts.runId;
  }

  /**
   * This should be called to clear the initial tree state and
   * get into a clean state.
   */
  clearAndInitializeTree() {
    this.resetState();
  }

  /**
   * Should be used to add the initial contents to the tree. After those are added
   * the contents appended afterwards are handled (in case a running
   * session is being tracked).
   */
  public async addInitialContents(): Promise<void> {
    const initial = this.opts.initialContents;
    if (initial === undefined) {
      this.finishedAddingInitialContents = true;
      return;
    }
    for (const msg of iter_decoded_log_format(initial, this.decoder)) {
      if (!this.isCurrentTreeBuilder()) {
        return;
      }
      await this.addOneMessage(msg);
    }
    this.finishedAddingInitialContents = true;
    await this.onAppendedContents();
  }

  /**
   * Used to add to the tree contents appended in real-time.
   */
  public async onAppendedContents(): Promise<void> {
    if (!this.finishedAddingInitialContents) {
      return;
    }
    if (!this.isCurrentTreeBuilder()) {
      return;
    }

    while (this.appendedMessagesIndex + 1 < this.opts.appendedContents.length) {
      this.appendedMessagesIndex += 1;
      const processMsg = this.opts.appendedContents[this.appendedMessagesIndex];
      for (const msg of iter_decoded_log_format(processMsg, this.decoder)) {
        if (!this.isCurrentTreeBuilder()) {
          return;
        }
        await this.addOneMessage(msg);
      }
    }

    // TODO: properly compute from where we should update (we have to
    // check what was the first item which was updated as we could be
    // changing previous entries when the element is being closed).
    const updateFromIndex = 0;
    setAllEntriesWhenPossible(this.flattened.entries, updateFromIndex);
    if (this.runInfoChanged) {
      this.runInfoChanged = false;
      setRunInfoWhenPossible(this.runInfo);
    }
  }

  private async addOneMessage(msg: IMessage): Promise<void> {
    // console.log("#", JSON.stringify(msg));

    if (!this.isCurrentTreeBuilder()) {
      return;
    }
    // Just making sure that the code below is all sync.
    try {
      this.addOneMessageSync(msg);
    } catch (err) {
      console.log(
        `Error: handling message: ${JSON.stringify(msg)}: ${err} - ${JSON.stringify(err)}`,
      );
      logError(err);
    }
  }

  private addOneMessageSync(msg: IMessage): void {
    let msgType = msg.message_type;
    switch (msgType) {
      // if it's a replay suite/test/keyword/exception, skip it if we've already seen
      // a suit/test/keyword/exception (otherwise, change the replay to the actual
      // type being replayed to have it properly handled).
      case 'SR':
      case 'ST':
      case 'SE':
      case 'STB':
        this.seenSuiteTaskOrElement = true;
        break;

      case 'RR':
        if (this.seenSuiteTaskOrElement) {
          return;
        }
        msgType = 'SR';
        break;
      case 'RT':
        if (this.seenSuiteTaskOrElement) {
          return;
        }
        msgType = 'ST';
        break;
      case 'RE':
        if (this.seenSuiteTaskOrElement) {
          return;
        }
        msgType = 'SE';
        break;
      case 'RTB':
        if (this.seenSuiteTaskOrElement) {
          return;
        }
        msgType = 'STB';
        break;
    }
    this.id += 1;

    switch (msgType) {
      case 'SR':
        // start run
        this.updateRunInfoName(msg.decoded['name']);
        break;

      case 'AS':
        // assign
        // item = addTreeContent(
        //   this.opts,
        //   this.parent,
        //   `${msg.decoded['target']} = `,
        //   `Assign to name: ${msg.decoded['target']}\nAn object of type: ${msg.decoded['type']}\nWith representation:\n${msg.decoded['value']}`,
        //   msg,
        //   false,
        //   msg.decoded['source'],
        //   msg.decoded['lineno'],
        //   this.messageNode,
        //   this.id.toString(),
        // );
        // addValueToTreeContent(item, msg.decoded['value']);
        // this.addAssignCssClass(item);
        break;
      case 'ST':
        // start task
        this.flattened.pushTaskScope(msg);
        break;
      case 'SE': // start element
        this.flattened.pushMethodScope(msg);
        break;
      case 'YR': // yield resume
      case 'YFR': // yield from resume
        // const raiseStack = msgType != 'SE' || msg.decoded['type'] != 'UNTRACKED_GENERATOR';
        // if (!raiseStack) {
        //   const item = addTreeContent(
        //     this.opts,
        //     this.parent,
        //     `Create Generator: ${msg.decoded['name']}`,
        //     '',
        //     msg,
        //     false,
        //     msg.decoded['source'],
        //     msg.decoded['lineno'],
        //     this.messageNode,
        //     this.id.toString(),
        //   );
        //   this.addGeneratorCSSClass(item);
        //   this.argsTarget = item;
        // } else {
        //   this.messageNode = { parent: this.messageNode, message: msg };
        //   let name = msg.decoded['name'];
        //   if (msgType == 'YR') {
        //     name += ' (resumed)';
        //   }
        //   this.parent = addTreeContent(
        //     this.opts,
        //     this.parent,
        //     name,
        //     msg.decoded['libname'],
        //     msg,
        //     false,
        //     msg.decoded['source'],
        //     msg.decoded['lineno'],
        //     this.messageNode,
        //     this.id.toString(),
        //   );
        //   if (msgType == 'YR') {
        //     this.addResumedCSSClass(this.parent);
        //   }

        //   this.argsTarget = this.parent;
        //   this.stack.push(this.parent);
        // }

        break;
      case 'ER': // end run
        if (this.suiteErrored) {
          this.updateRunInfoStatus('ERROR');
        } else {
          this.updateRunInfoStatus('PASS');
        }
        this.updateRunInfoFinishTime(msg.decoded['time_delta_in_seconds']);
        //   const timeDiv = divById('suiteRunStart');
        //   if (timeDiv) {
        //     timeDiv.textContent += ` - Finished in: ${msg.decoded['time_delta_in_seconds'].toFixed(
        //       2,
        //     )}s.`;
        //   }
        // }
        break;
      case 'ET': // end task
        this.flattened.popTaskScope(msg);
        break;
      case 'EE': // end element
        this.flattened.popMethodScope(msg);
        break;
      case 'YS': // yield suspend
      case 'YFS': // yield from suspend
        // const popStack = msgType != 'EE' || msg.decoded['type'] != 'UNTRACKED_GENERATOR';
        // if (!popStack) {
        //   // The generator finished, but we don't even have its name... maybe we should have
        //   // a different message for this case?
        // } else {
        //   if (msgType == 'YS' || msgType == 'YFS') {
        //     const yieldedItem = addTreeContent(
        //       this.opts,
        //       this.parent,
        //       'Yielded',
        //       `Suspending function with yield.\nYielding an object of type: ${msg.decoded['type']}\nWith representation:\n${msg.decoded['value']}`,
        //       msg,
        //       false,
        //       msg.decoded['source'],
        //       msg.decoded['lineno'],
        //       this.messageNode,
        //       this.id.toString(),
        //     );
        //     this.addYieldedCSSClass(yieldedItem);
        //     addValueToTreeContent(yieldedItem, msg.decoded['value']);
        //     msg.decoded['status'] = 'PASS';
        //   }

        //   this.messageNode = this.messageNode.parent;
        //   let currK = this.parent;

        //   this.stack.pop();
        //   this.parent = this.stack.at(-1);
        //   this.onEndUpdateMaxLevelFoundInHierarchyFromStatus(currK, this.parent, msg);
        //   this.onEndSetStatusOrRemove(this.opts, currK, msg.decoded, this.parent, true);

        //   isError = this.addDetailsCSSClasses(msg.decoded.status, currK);
        //   if (isError) {
        //     currK.details.open = true;
        //   }
        // }

        break;
      case 'S':
        // Update the start time from the current message.
        // const start = msg.decoded['start_time_delta'];
        // if (this.parent?.decodedMessage?.decoded) {
        //   this.parent.decodedMessage.decoded['time_delta_in_seconds'] = start;
        // }
        break;
      case 'EA':
        // Element arguments
        this.flattened.addArguments(msg);
        break;
      case 'L':
      case 'LH':
        // A bit different because it's always leaf and based on 'level', not 'status'.
        // const level = msg.decoded['level'];
        // const iLevel = getIntLevelFromLevelStr(level);
        // if (iLevel > this.parent.maxLevelFoundInHierarchy) {
        //   this.parent.maxLevelFoundInHierarchy = iLevel;
        //   // console.log("set level", parent.decodedMessage, "to", iLevel);
        // }
        // if (acceptLevel(this.opts, iLevel)) {
        //   const logContent = addTreeContent(
        //     this.opts,
        //     this.parent,
        //     msg.decoded['message'],
        //     '',
        //     msg,
        //     false,
        //     msg.decoded['source'],
        //     msg.decoded['lineno'],
        //     this.messageNode,
        //     this.id.toString(),
        //   );
        //   logContent.maxLevelFoundInHierarchy = iLevel;
        //   addLevel(logContent, level);
        //   this.addDetailsCSSClasses(iLevel, logContent);
        // }
        break;
      case 'STB': // start
      case 'TBE': // tb entry
      case 'TBV': // variable
      case 'ETB': // tb end
        const tb: PythonTraceback | undefined = this.tbHandler.handle(msg);
        if (tb) {
          if (tb.stack.length > 0) {
            const tbEntry = tb.stack[0];
            const split: string[] = tb.exceptionMsg.split(':', 2);
            let excType: string;
            let excMsg: string;
            if (split.length > 1) {
              excType = split[0];
              excMsg = split[1];
            } else {
              excType = 'Error';
              excMsg = split[0];
            }

            // item = addTreeContent(
            //   this.opts,
            //   this.parent,
            //   excType,
            //   '',
            //   msg,
            //   false,
            //   tbEntry.source,
            //   tbEntry.lineno,
            //   this.messageNode,
            //   this.id.toString(),
            // );
            // addValueToTreeContent(item, excMsg);
            // this.addExceptionCssClass(item);
          }
        }
        break;
      case 'T':
        this.updateRunInfoTime(msg.decoded);
        break;
    }
  }
}

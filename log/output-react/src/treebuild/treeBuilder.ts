import { Type, EntryBase, EntryTask } from '../lib/types';
import { Decoder, iter_decoded_log_format, IMessage } from './decoder';
import { getOpts } from './options';
import { IOpts, PythonTraceback } from './protocols';
import { getIntLevelFromStatus } from './status';

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
  public entries: EntryBase[] = [];

  public stack: EntryBase[] = [];

  private parentId = 'root';

  private seqId = 0;

  newScopeId(): string {
    this.seqId += 1;
    const newId = `${this.parentId}-${this.seqId}`;
    this.parentId = newId;
    return newId;
  }

  pushTaskScope(msg: IMessage) {
    const entry: EntryTask = {
      id: this.newScopeId(),
      type: Type.task,
      name: `${msg.decoded.libname}.${msg.decoded.name}`,
      value: '',
      source: msg.decoded.source,
      lineno: msg.decoded.lineno,
      endDeltaInSeconds: -1,
      startDeltaInSeconds: msg.decoded.time_delta_in_seconds,
    };
    this.stack.push(entry);
    this.entries.push(entry);
  }

  popTaskScope(msg: IMessage) {
    let entry: EntryBase | undefined;
    while (true) {
      if (this.stack.length === 0) {
        console.log(
          `Unable to find task start when receiving end task message: ${JSON.stringify(msg)}.`,
        );
      }
      entry = this.stack.pop();
      if (entry?.type === Type.task) {
        break;
      }
    }
    const taskScopeEntry: EntryTask = <EntryTask>entry;

    const { status } = msg.decoded;
    const iLevel = getIntLevelFromStatus(status);
    taskScopeEntry.endDeltaInSeconds = msg.decoded.time_delta_in_seconds;
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

  constructor() {
    this.opts = getOpts();
    this.runId = this.opts.runId;
    this.lease = obtainNewLease();
    this.resetState();
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

    const opts = getOpts();
    while (this.appendedMessagesIndex + 1 < opts.appendedContents.length) {
      this.appendedMessagesIndex += 1;
      const processMsg = opts.appendedContents[this.appendedMessagesIndex];
      for (const msg of iter_decoded_log_format(processMsg, this.decoder)) {
        if (!this.isCurrentTreeBuilder()) {
          return;
        }
        await this.addOneMessage(msg);
      }
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
        // TODO: Set suite header
        // for (const el of document.querySelectorAll('.suiteHeader')) {
        //   el.textContent = msg.decoded['name'];
        // }

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
        // this.messageNode = this.messageNode.parent;
        // {
        //   const div = divById('suiteResult');
        //   div.style.display = 'block';
        //   if (this.suiteErrored) {
        //     div.classList.add('ERROR');
        //     div.textContent = 'Run Failed';
        //   } else {
        //     div.classList.add('PASS');
        //     div.textContent = 'Run Passed';
        //   }

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
        // addArgumentsToTreeContent(
        //   this.argsTarget,
        //   msg.decoded['name'],
        //   msg.decoded['type'],
        //   msg.decoded['value'],
        // );
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
        // const div = divById('suiteRunStart');
        // if (div) {
        //   div.textContent = msg.decoded['time'];
        // }
        break;
    }
  }
}

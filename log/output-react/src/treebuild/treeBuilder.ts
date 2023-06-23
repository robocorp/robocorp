import {
  Type,
  EntryBase,
  EntryTask,
  Entry,
  StatusLevel,
  EntryMethod,
  Argument,
  EntryException,
  EntryVariable,
  EntryUntrackedGenerator,
  EntryMethodBase,
  EntryGenerator,
  EntryResumeYield,
  EntryResumeYieldFrom,
  EntrySuspendYield,
  EntrySuspendYieldFrom,
  EntryLog,
  ConsoleMessageKind,
  EntryThreadDump,
  EntryProcessSnapshot,
  EntryIf,
  EntryElse,
  EntryReturn,
} from '../lib/types';
import { setAllEntriesWhenPossible, setRunInfoWhenPossible } from './effectCallbacks';
import { Decoder, iter_decoded_log_format, IMessage, splitInChar, SPEC_RESTARTS } from './decoder';
import { IOpts, ITracebackEntry, PythonTraceback } from './protocols';
import { getIntLevelFromStatus } from './status';
import { Counter, RunInfo, RunInfoStatus, createDefaultRunInfo, logError } from '../lib';

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
      case 'STB': // start traceback
      case 'STD': // start thread dump
        this.stack.push(new PythonTraceback(msg.decoded.message));
        return undefined;

      case 'TBE': // tb entry
        tb = this.stack.at(-1);
        if (tb === undefined) {
          console.log('Unable add traceback entry because no traceback is in the stack.');
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
        tb = this.stack.at(-1);
        if (tb === undefined) {
          console.log('Unable add traceback variable because no traceback is in the stack.');
          return undefined;
        }
        tb.pushVar(msg.decoded['name'], msg.decoded['type'], msg.decoded['value']);
        return undefined;

      case 'ETB': // tb end
      case 'ETD': // thread dump end
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
  // All entries we're viewing.
  // Note: when an entry is changed a copy should be done and the entry
  // in this object should be replace.
  public entries: Entry[] = [];

  // New entry ids which should be automatically expanded.
  public newExpanded: string[] = [];

  // A stack to help us manage the parent entry for new entries.
  // Note: when an entry is changed a copy should be done and the entry
  // in this object should be replace.
  public stack: Entry[] = [];

  // A stack helper just to provide ids for entries.
  public stackCounter: Counter[] = [new Counter()];

  // The target for the arguments being set (may not be the stack top as some
  // entries which have arguments may not create a new scope).
  private argsTarget: EntryMethodBase | undefined;

  // The current parentId.
  private parentId = '';

  newScopeId(addToStack = true): string {
    let counter = this.stackCounter.at(-1);
    if (counter === undefined) {
      throw new Error('Error stack counter must always have at least 1 entry.');
    }
    const newId =
      this.parentId.length === 0 ? `root${counter.next()}` : `${this.parentId}-${counter.next()}`;

    if (addToStack) {
      this.parentId = newId;
      this.stackCounter.push(new Counter());
    }

    return newId;
  }

  pushException(tb: PythonTraceback) {
    const tbEntry: ITracebackEntry = tb.stack[0];
    const split: string[] | undefined = splitInChar(tb.exceptionMsg, ':');
    let excType: string;
    let excMsg: string;
    if (split !== undefined) {
      excType = split[0];
      excMsg = split[1];
    } else {
      excType = 'Error';
      excMsg = tb.exceptionMsg;
    }
    const entry: EntryException = {
      id: this.newScopeId(false),
      type: Type.exception,
      source: tbEntry.source,
      lineno: tbEntry.lineno,
      tb: tb,
      excType: excType,
      excMsg: excMsg.trim(),
      entriesIndex: this.entries.length,
    };
    this.entries.push(entry);
  }

  pushThreadDump(tb: PythonTraceback) {
    const tbEntry: ITracebackEntry = tb.stack[0];
    const split: string[] | undefined = splitInChar(tb.exceptionMsg, '|');
    let threadName: string;
    let threadDetails: string;
    if (split !== undefined) {
      threadName = split[0];
      threadDetails = split[1];
    } else {
      threadName = '<unknown thread name>';
      threadDetails = tb.exceptionMsg;
    }
    const entry: EntryThreadDump = {
      id: this.newScopeId(false),
      type: Type.threadDump,
      source: tbEntry.source,
      lineno: tbEntry.lineno,
      tb: tb,
      threadName,
      threadDetails: threadDetails.trim(),
      entriesIndex: this.entries.length,
    };
    this.entries.push(entry);
  }

  pushConsole(msg: IMessage) {
    // TODO: See what to do with the console messages.
    let internalLogKind: ConsoleMessageKind = ConsoleMessageKind.unset;

    switch (msg.decoded['kind']) {
      case 'regular':
        internalLogKind = ConsoleMessageKind.regular;
        break;

      // These ones are generated by the framework and are skipped for now.
      case 'stdout:':
      case 'stderr':
      case 'important':
      case 'task_name':
      case 'error':
      case 'traceback':
        return;
    }
  }

  pushLog(msg: IMessage) {
    let level: StatusLevel = StatusLevel.unset;

    switch (msg.decoded['level']) {
      case 'E':
      case 'F':
        level = StatusLevel.error;
        break;
      case 'W':
        level = StatusLevel.warn;
        break;
      case 'I':
        level = StatusLevel.info;
        break;
    }

    const entry: EntryLog = {
      id: this.newScopeId(false),
      type: Type.log,
      status: level,
      message: msg.decoded['message'],
      source: msg.decoded['source'],
      lineno: msg.decoded['lineno'],
      isHtml: msg.message_type === 'LH',
      entriesIndex: this.entries.length,
    };
    this.entries.push(entry);
  }

  pushUntrackedGeneratorScope(msg: IMessage) {
    const entry: EntryUntrackedGenerator = {
      id: this.newScopeId(false),
      type: Type.untrackedGenerator,
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
    this.entries.push(entry);
    this.argsTarget = entry;
  }

  pushIf(msg: IMessage) {
    const entry: EntryIf = {
      id: this.newScopeId(false),
      type: Type.ifElement,
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
    this.entries.push(entry);
    this.argsTarget = entry;
  }

  pushElse(msg: IMessage) {
    const entry: EntryElse = {
      id: this.newScopeId(false),
      type: Type.elseElement,
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
    this.entries.push(entry);
    this.argsTarget = entry;
  }

  pushYieldSuspend(msg: IMessage) {
    // Tooltip
    // `Suspending function with yield.\nYielding an object of type: ${msg.decoded['type']}\nWith representation:\n${msg.decoded['value']}`,
    const isYieldFrom = msg.message_type == 'YFS';
    const entry: EntrySuspendYield | EntrySuspendYieldFrom = {
      id: this.newScopeId(false),
      type: isYieldFrom ? Type.suspendYieldFrom : Type.suspendYield,
      name: msg.decoded.name,
      libname: msg.decoded.libname,
      source: msg.decoded.source,
      lineno: msg.decoded.lineno,
      endDeltaInSeconds: -1,
      status: StatusLevel.unset,
      startDeltaInSeconds: msg.decoded.time_delta_in_seconds,
      entriesIndex: this.entries.length,
      arguments: undefined,
      varType: msg.decoded['type'], // Note: not really used for EntrySuspendYieldFrom.
      value: msg.decoded['value'], // Note: not really used for EntrySuspendYieldFrom.
    };
    this.entries.push(entry);
    this.argsTarget = entry;
  }

  pushMethodScope(msg: IMessage) {
    const isGenerator = msg.decoded['type'] === 'GENERATOR';
    const entry: EntryMethod | EntryGenerator = {
      id: this.newScopeId(),
      type: isGenerator ? Type.generator : Type.method,
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

  pushResumeMethodScope(msg: IMessage) {
    const isYieldFrom = msg.message_type == 'YFR';
    const entry: EntryResumeYield | EntryResumeYieldFrom = {
      id: this.newScopeId(),
      type: isYieldFrom ? Type.resumeYieldFrom : Type.resumeYield,
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

  pushAssign(msg: IMessage) {
    const entry: EntryVariable = {
      id: this.newScopeId(false),
      type: Type.variable,
      source: msg.decoded['source'],
      lineno: msg.decoded['lineno'],
      name: msg.decoded['target'],
      value: msg.decoded['value'],
      varType: msg.decoded['type'],
      entriesIndex: this.entries.length,
    };
    this.entries.push(entry);
    // Tooltip:
    // `Assign to name: ${msg.decoded['target']}\nAn object of type: ${msg.decoded['type']}\nWith representation:\n${msg.decoded['value']}`,
  }

  pushReturn(msg: IMessage) {
    const entry: EntryReturn = {
      id: this.newScopeId(false),
      type: Type.returnElement,
      name: msg.decoded.name,
      libname: msg.decoded.libname,
      source: msg.decoded['source'],
      lineno: msg.decoded['lineno'],
      value: msg.decoded['value'],
      varType: msg.decoded['type'],
      entriesIndex: this.entries.length,
    };
    this.entries.push(entry);
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

  pushProcessSnapshotScope(msg: IMessage) {
    // console.log('pushProcessSnapshotScope');
    const entry: EntryProcessSnapshot = {
      id: this.newScopeId(),
      type: Type.processSnapshot,
      endDeltaInSeconds: -1,
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
      if (entry === undefined) {
        continue;
      }
      if ((entry.type & type) != 0) {
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
      } else {
        console.log(
          `Unable to find scope start when receiving end message: ${JSON.stringify(
            msg,
          )}. Entry popped: ${JSON.stringify(entry)}`,
        );
      }
    }
    return entry;
  }

  updateEntryStatus(entry: EntryTask | EntryMethod, msg: IMessage) {
    const { status } = msg.decoded;
    entry.status = getIntLevelFromStatus(status);
    entry.endDeltaInSeconds = msg.decoded.time_delta_in_seconds;

    this.entries[entry.entriesIndex] = entry;
    if (entry.status >= StatusLevel.error) {
      this.newExpanded.push(entry.id);
    }
  }

  popMethodScope(msg: IMessage) {
    // Note: create a copy and assign it in the entries array (we don't want to mutate the
    // entry that's being used in react).
    const entry: EntryBase | undefined = this.popScope(
      msg,
      Type.method | Type.generator | Type.resumeYield | Type.resumeYieldFrom,
    );
    if (entry === undefined) {
      return;
    }

    if (msg.decoded.status === undefined) {
      // No need to update if the status isn't set.
      return;
    }
    const methodScopeEntry: EntryMethod = <EntryMethod>{ ...entry };
    this.updateEntryStatus(methodScopeEntry, msg);
  }

  popTaskScope(msg: IMessage): EntryTask | undefined {
    const entry: EntryBase | undefined = this.popScope(msg, Type.task);
    if (entry === undefined) {
      return;
    }

    // Note: create a copy and assign it in the entries array (we don't want to mutate the
    // entry that's being used in react).
    const taskScopeEntry: EntryTask = <EntryTask>{ ...entry };
    this.updateEntryStatus(taskScopeEntry, msg);
    return taskScopeEntry;
  }

  popProcessSnapshotScope(msg: IMessage) {
    const entry: EntryBase | undefined = this.popScope(msg, Type.processSnapshot);
    if (entry === undefined) {
      return;
    }

    // Note: create a copy and assign it in the entries array (we don't want to mutate the
    // entry that's being used in react).
    const processSnapshotEntry: EntryProcessSnapshot = <EntryProcessSnapshot>{ ...entry };
    processSnapshotEntry.endDeltaInSeconds = msg.decoded.time_delta_in_seconds;
    this.entries[processSnapshotEntry.entriesIndex] = processSnapshotEntry;
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
    this.updateSpecRestartInfo();
    this.resetState();
  }

  private runInfo: RunInfo = createDefaultRunInfo();

  private runInfoChanged: boolean = false;

  updateRunInfoName(name: string) {
    this.runInfo.description = name;
    this.runInfoChanged = true;
  }

  updateRunInfoTime(time: string) {
    this.runInfo.time = time;
    this.runInfoChanged = true;
  }

  updateID(id: IMessage) {
    const part = id.decoded['part'];
    if (this.runInfo.firstPart === -1) {
      this.runInfo.firstPart = part;
    }
    this.runInfo.lastPart = part;
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
    let newExpanded = this.flattened.newExpanded;
    if (newExpanded.length > 0) {
      // Don't add the same ones again.
      this.flattened.newExpanded = [];
    }
    setAllEntriesWhenPossible(this.flattened.entries, newExpanded, updateFromIndex);
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

  restartMsgToOriginalMsgType = new Map<string, string>();
  regularContextMsgType = new Set<string>();

  private updateSpecRestartInfo() {
    const restartMsgToOriginalMsgType = new Map<string, string>();
    const regularContextMsgType = new Set<string>();

    for (let line of SPEC_RESTARTS.split(/\r?\n/)) {
      line = line.trim();
      if (line.length === 0 || line.startsWith('#')) {
        continue;
      }
      const split2 = splitInChar(line, '=');
      if (split2 === undefined) {
        throw new Error(`Unable to split on ':' and '=' in ${line}.`);
      } else {
        let [key, val] = split2;
        key = key.trim();
        val = val.trim();
        restartMsgToOriginalMsgType.set(key, val);
        regularContextMsgType.add(val);
      }
    }
    this.restartMsgToOriginalMsgType = restartMsgToOriginalMsgType;
    this.regularContextMsgType = regularContextMsgType;
  }

  private addOneMessageSync(msg: IMessage): void {
    let msgType = msg.message_type;
    if (this.regularContextMsgType.has(msgType)) {
      this.seenSuiteTaskOrElement = true;
    }
    const translated = this.restartMsgToOriginalMsgType.get(msgType);
    // if it's a replay suite/test/keyword/exception, skip it if we've already seen
    // a suit/test/keyword/exception (otherwise, change the replay to the actual
    // type being replayed to have it properly handled).
    if (translated !== undefined) {
      // msgType is a replay
      if (this.seenSuiteTaskOrElement) {
        // We've already seen a regular message. Ignore it.
        return;
      }
      msgType = translated;
    }
    this.id += 1;

    switch (msgType) {
      case 'ID':
        this.updateID(msg);
        break;
      case 'SR':
        // start run
        this.updateRunInfoName(msg.decoded['name']);
        break;

      case 'AS':
        // assign
        this.flattened.pushAssign(msg);
        break;
      case 'R':
        // return
        this.flattened.pushReturn(msg);
        break;
      case 'ST':
        // start task
        this.flattened.pushTaskScope(msg);
        break;
      case 'SPS':
        // start process snapshot
        this.flattened.pushProcessSnapshotScope(msg);
        break;
      case 'SE': // start element
        if (msg.decoded['type'] === 'UNTRACKED_GENERATOR') {
          this.flattened.pushUntrackedGeneratorScope(msg);
        } else if (msg.decoded['type'] === 'IF') {
          this.flattened.pushIf(msg);
        } else if (msg.decoded['type'] === 'ELSE') {
          this.flattened.pushElse(msg);
        } else {
          this.flattened.pushMethodScope(msg);
        }

        break;
      case 'YR': // yield resume
      case 'YFR': // yield from resume
        this.flattened.pushResumeMethodScope(msg);
        break;
      case 'ER': // end run
        if (this.suiteErrored) {
          this.updateRunInfoStatus('ERROR');
        } else {
          this.updateRunInfoStatus('PASS');
        }
        this.updateRunInfoFinishTime(msg.decoded['time_delta_in_seconds']);
        break;
      case 'ET': // end task
        const taskScope = this.flattened.popTaskScope(msg);
        if (taskScope !== undefined) {
          if (taskScope.status >= StatusLevel.error) {
            this.suiteErrored = true;
          }
        }
        break;
      case 'EE': // end element
        if (msg.decoded['type'] === 'UNTRACKED_GENERATOR') {
          // The generator finished, but we don't even have its name... maybe we should have
          // a different message for this case?
        } else {
          const isGenerator = msg.decoded['type'] === 'GENERATOR';
          this.flattened.popMethodScope(msg);
        }
        break;
      case 'EPS':
        // end process snapshot
        this.flattened.popProcessSnapshotScope(msg);
        break;
      case 'YS': // yield suspend
      case 'YFS': // yield from suspend
        const isYieldFrom = msg.message_type == 'YFS';
        this.flattened.pushYieldSuspend(msg);
        this.flattened.popMethodScope(msg);
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
        this.flattened.pushLog(msg);
        break;
      case 'STB': // start traceback
      case 'STD': // start thread dump
      case 'TBE': // tb entry
      case 'TBV': // variable
      case 'ETB': // tb end
      case 'ETD': // thread dump end
        const tb: PythonTraceback | undefined = this.tbHandler.handle(msg);
        if (tb) {
          if (tb.stack.length > 0) {
            if (msgType === 'ETB') {
              // traceback means exception
              this.flattened.pushException(tb);
            } else if (msgType === 'ETD') {
              // thread dump
              this.flattened.pushThreadDump(tb);
            }
          }
        }
        break;
      case 'T':
        this.updateRunInfoTime(msg.decoded);
        break;
    }
  }
}

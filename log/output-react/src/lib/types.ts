import { PythonTraceback } from '~/treebuild/protocols';

export type FormatType = 'auto' | 'raw' | 'pretty';

export interface TreeFilterInfo {
  showInTree: StatusLevel; // Actually an or(StatusLevel)
}

export type ViewSettings = {
  columns: {
    duration: boolean;
    location: boolean;
  };
  theme: 'dark' | 'light';
  format: FormatType;
  mode: 'compact' | 'sparse';
  showInTerminal: StatusLevel; // Actually an or(StatusLevel)
  treeFilterInfo: TreeFilterInfo;
};

export interface InfoForScroll {
  mode: 'scrollToItem' | 'scrollToChildren';
  scrollTargetId: string;
  idDepth: number;
  entriesInfo: undefined | EntriesInfo;
  mtime: number;
}

export interface TreeEntries {
  entries: Entry[];
  entriesWithChildren: Set<string>;
  idToEntryIndexInTreeArray: Map<string, number>;
}

export interface GetEntryFromId {
  (id: string): Entry | undefined;
}

export interface EntriesAndIdToEntry {
  allEntries: Entry[];
  idToEntry: Map<string, Entry>;
}

/**
 * Entries go through a bunch of filters and
 * different places may need it in different
 * representations, so, keep them all in this
 * structure.
 */
export interface EntriesInfo {
  // Easy: all the entries we have.
  allEntries: Entry[];

  // The first thing we do with the entries
  // is apply any needed filter to remove items
  // that the user doesn't want to see (i.e.:
  // remove status == debug)
  entriesWithFilterApplied: Entry[];

  // The last thing is actually the entries which
  // will actually be shown. These entries don't
  // have elements which are collapsed.
  treeEntries: TreeEntries;

  // A map with all entries mapping from the
  // entry id to the actual entry.
  getEntryFromId: GetEntryFromId;
}

export const getIndexInTree = (entriesInfo: EntriesInfo, entry: Entry): number | undefined => {
  return entriesInfo.treeEntries.idToEntryIndexInTreeArray.get(entry.id);
};

export const createDefaultEntriesInfo = (): EntriesInfo => {
  return {
    allEntries: [],
    getEntryFromId: (id: string) => {
      return undefined;
    },
    entriesWithFilterApplied: [],
    treeEntries: {
      entries: [],
      entriesWithChildren: new Set(),
      idToEntryIndexInTreeArray: new Map(),
    },
  };
};

export enum StatusLevel {
  error = 1 << 4, // 16
  warn = 1 << 3, // 8
  info = 1 << 2, // 4
  debug = 1 << 1, // 2
  success = 1,
  unset = 0,
}

export enum Type {
  task = 1 << 0, // 1
  variable = 1 << 1, // 2
  method = 1 << 2, // 4
  exception = 1 << 3, // 8
  generator = 1 << 4, // 16
  untrackedGenerator = 1 << 5, // 32
  resumeYieldFrom = 1 << 6, // 64
  resumeYield = 1 << 7, // 128
  suspendYieldFrom = 1 << 8, // 256
  suspendYield = 1 << 9, // 512
  log = 1 << 10, // 1024
  threadDump = 1 << 11, // 2048
  processSnapshot = 1 << 12, // 4096
  ifElement = 1 << 13,
  elseElement = 1 << 14,
  returnElement = 1 << 15, // 32768
  console = 1 << 16,
  assertFailed = 1 << 17,
  continueElement = 1 << 18,
  breakElement = 1 << 19,

  unhandled = 1 << 20,
}

export enum ConsoleMessageKind {
  unset = 0,
  regular = 1 << 1, // 1
  stdout = 1 << 2, // 2
  stderr = 1 << 3, // 4
  important = 1 << 5, // 8
  task_name = 1 << 6, // 16
  error = 1 << 7, // 32
  traceback = 1 << 8, // 64
  processSnapshot = 1 << 9, // 128
}

export interface EntryBase {
  id: string;
  type: Type;
  entryIndexAll: number; // this is the index in the full array.
}

export interface EntryWithLocationBase extends EntryBase {
  source: string;
  lineno: number;
}

export interface EntryTask extends EntryWithLocationBase {
  type: Type.task;
  name: string;
  libname: string;
  status: StatusLevel;
  startDeltaInSeconds: number | -1 | undefined;
  endDeltaInSeconds: number | -1 | undefined;
}

export interface EntryProcessSnapshot extends EntryBase {
  type: Type.processSnapshot;
  startDeltaInSeconds: number | -1 | undefined;
  endDeltaInSeconds: number | -1 | undefined;
}

export interface Argument {
  name: string;
  type: string;
  value: string;
}

export interface EntryMethodBase extends EntryWithLocationBase {
  name: string;
  libname: string;
  status: StatusLevel;
  startDeltaInSeconds: number | -1 | undefined;
  endDeltaInSeconds: number | -1 | undefined;
  arguments: Argument[] | undefined;
}

export interface EntryMethod extends EntryMethodBase {
  type: Type.method;
}

export interface EntryGenerator extends EntryMethodBase {
  type: Type.generator;
}

export interface EntryUntrackedGenerator extends EntryMethodBase {
  type: Type.untrackedGenerator;
}

export interface EntryResumeYield extends EntryMethodBase {
  type: Type.resumeYield;
}

export interface EntryResumeYieldFrom extends EntryMethodBase {
  type: Type.resumeYieldFrom;
}

export interface EntryContinue extends EntryMethodBase {
  type: Type.continueElement;
}

export interface EntryBreak extends EntryMethodBase {
  type: Type.breakElement;
}

export interface EntryIf extends EntryMethodBase {
  type: Type.ifElement;
}

export interface EntryElse extends EntryMethodBase {
  type: Type.elseElement;
}

export interface EntryAssertFailed extends EntryMethodBase {
  type: Type.assertFailed;
}

export interface EntrySuspendYield extends EntryMethodBase {
  type: Type.suspendYield;
  value: string; // the yielded value
  varType: string;
}

export interface EntrySuspendYieldFrom extends EntryMethodBase {
  type: Type.suspendYieldFrom;
}

export interface EntryException extends EntryWithLocationBase {
  tb: PythonTraceback;
  excType: string;
  excMsg: string;
}

export interface EntryThreadDump extends EntryWithLocationBase {
  tb: PythonTraceback;
  threadName: string;
  threadDetails: string;
}

export interface EntryVariable extends EntryWithLocationBase {
  type: Type.variable;
  name: string;
  value: string;
  varType: string;
}

export interface EntryReturn extends EntryWithLocationBase {
  type: Type.returnElement;
  name: string;
  libname: string;
  value: string;
  varType: string;
}

export interface EntryLog extends EntryWithLocationBase {
  type: Type.log;
  status: StatusLevel;
  isHtml: boolean;
  message: string;
}

export interface EntryConsole extends EntryWithLocationBase {
  type: Type.console;
  kind: ConsoleMessageKind;
  message: string;
}

export type Entry =
  | EntryTask
  | EntryMethod
  | EntryVariable
  | EntryLog
  | EntryException
  | EntryGenerator
  | EntryResumeYield
  | EntryResumeYieldFrom
  | EntrySuspendYield
  | EntrySuspendYieldFrom
  | EntryUntrackedGenerator
  | EntryThreadDump
  | EntryIf
  | EntryElse
  | EntryReturn
  | EntryConsole
  | EntryProcessSnapshot
  | EntryBreak
  | EntryContinue
  | EntryAssertFailed;

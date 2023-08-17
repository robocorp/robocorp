import { IsExpanded } from './logContext';
import {
  ConsoleMessageKind,
  Entry,
  EntryConsole,
  EntryElse,
  EntryException,
  EntryGenerator,
  EntryIf,
  EntryLog,
  EntryMethod,
  EntryMethodBase,
  EntryResumeYield,
  EntryResumeYieldFrom,
  EntrySuspendYield,
  EntrySuspendYieldFrom,
  EntryTask,
  EntryUntrackedGenerator,
  EntryWithLocationBase,
  TreeEntries,
  StatusLevel,
  Type,
} from './types';
import * as DOMPurify from 'dompurify';

export function entryDepth(entry: Entry) {
  return entryIdDepth(entry.id);
}

export function entryIdDepth(id: string) {
  return id.split('-').length - 1;
}

export function entryIdParent(id: string): string | undefined {
  const i = id.lastIndexOf('-');
  let parentId: string | undefined = undefined;
  if (i > 0) {
    parentId = id.substring(0, i);
  }
  return parentId;
}

export function truncateString(str: string, maxLength: number): string {
  if (str.length <= maxLength) {
    return str;
  } else {
    return str.substring(0, maxLength - 3) + '...';
  }
}

export const findMinAndMax = (numbers: number[]): [number, number] => {
  if (numbers.length === 0) {
    throw new Error('Array is empty');
  }
  let min = numbers[0];
  let max = numbers[0];

  for (let i = 1; i < numbers.length; i++) {
    if (numbers[i] < min) {
      min = numbers[i];
    }
    if (numbers[i] > max) {
      max = numbers[i];
    }
  }

  return [min, max];
};

export class IDChecker {
  private parentParts: string[];

  constructor(parentId: string) {
    this.parentParts = parentId.split('-');
  }

  isParentOf(childId: string): boolean {
    const childParts = childId.split('-');

    if (childParts.length < this.parentParts.length) {
      return false;
    }

    for (let i = 0; i < this.parentParts.length; i++) {
      if (this.parentParts[i] !== childParts[i]) {
        return false;
      }
    }

    return true;
  }
}

/**
 * In the tree some console entries should not appear.
 */
export const acceptConsoleEntryInTree = (kind: ConsoleMessageKind, message: string) => {
  if (kind !== ConsoleMessageKind.stdout && kind !== ConsoleMessageKind.stderr) {
    return false;
  }
  // Also remove empty messages from the tree.
  if (message.trim().length === 0) {
    return false;
  }
  return true;
};

/**
 * Provides the status level to be considered for some entry.
 */
export const getStatusLevel = (entry: Entry): StatusLevel => {
  switch (entry.type) {
    case Type.task:
      const entryTask: EntryTask = entry as EntryTask;
      return entryTask.status;
    case Type.method:
      return (entry as EntryMethod).status;
    case Type.ifElement:
      return (entry as EntryIf).status;
    case Type.elseElement:
      return (entry as EntryElse).status;
    case Type.generator:
      return (entry as EntryGenerator).status;
    case Type.untrackedGenerator:
      return (entry as EntryUntrackedGenerator).status;
    case Type.resumeYield:
      return (entry as EntryResumeYield).status;
    case Type.resumeYieldFrom:
      return (entry as EntryResumeYieldFrom).status;
    case Type.suspendYield:
      return (entry as EntrySuspendYield).status;
    case Type.suspendYieldFrom:
      return (entry as EntrySuspendYieldFrom).status;
    case Type.returnElement:
    case Type.continueElement:
    case Type.breakElement:
      return StatusLevel.info;
    case Type.variable:
      return StatusLevel.info;
    case Type.assertFailed:
      return StatusLevel.error;
    case Type.log:
      const log: EntryLog = entry as EntryLog;
      return log.status;
    case Type.console:
      const c: EntryConsole = entry as EntryConsole;
      switch (c.kind) {
        case ConsoleMessageKind.error:
        case ConsoleMessageKind.stderr:
        case ConsoleMessageKind.traceback:
          return StatusLevel.error;
        default:
          return StatusLevel.info;
      }
    case Type.exception:
      return StatusLevel.error;
    case Type.processSnapshot:
      return StatusLevel.info;
    case Type.threadDump:
      return StatusLevel.info;
    default:
      // TODO: Provide status level for missing element
      console.log('TODO: Provide status level for', entry);
      return StatusLevel.unset;
  }
};

export const leaveOnlyExpandedEntries = (data: Entry[], isExpanded: IsExpanded): TreeEntries => {
  // console.log('All: ', JSON.stringify(data));

  const entriesWithChildren: Set<string> = new Set();

  const ret: Entry[] = [];

  const idToEntryIndexInTreeArray: Map<string, number> = new Map();

  // We have to remove all non-expanded objects with
  // as little work as possible. Given that we have
  // a flattened list we take advantage of the knowledge
  // that items must appear in order in a tree-like order
  // where we'd traverse the parent and then its children
  // before going to the next parent and then automatically marking
  // children as hidden if the parent is hidden.
  let hideChildren: boolean = false;
  let hideChildrenOnDepth: number = 0;

  for (const entry of data) {
    if (entry.type === Type.console) {
      // We just want to show stdout and stderr entries.
      const entryConsole = entry as EntryConsole;
      if (!acceptConsoleEntryInTree(entryConsole.kind, entryConsole.message)) {
        continue;
      }
    }
    const depth = entryDepth(entry);
    const i = entry.id.lastIndexOf('-');
    let parentId: string | undefined = undefined;
    if (i > 0) {
      parentId = entry.id.substring(0, i);
      entriesWithChildren.add(parentId);
    }

    if (hideChildren) {
      if (depth > hideChildrenOnDepth) {
        // A child of the current entry we're hiding must be hidden.
        continue;
      }
      hideChildren = false;
    }

    idToEntryIndexInTreeArray.set(entry.id, ret.length);
    ret.push(entry);

    if (!isExpanded(entry.id)) {
      // i.e.: the current item is hidden: hide it and all its children
      // until we get to the next sibling.
      // Note that the item itself is still shown, just children are hidden.
      hideChildren = true;
      hideChildrenOnDepth = depth;
    }
  }
  // console.log('Filtered: ', JSON.stringify(ret));
  return { entries: ret, entriesWithChildren, idToEntryIndexInTreeArray };
};

export const formatLocation = (entry: Entry) => {
  if (Object.hasOwn(entry, 'source')) {
    const entryWithLocation = entry as EntryWithLocationBase;
    if (entryWithLocation.source) {
      if (entryWithLocation.lineno > 0) {
        return `${pathBasenameNoExt(entryWithLocation.source)}:${entryWithLocation.lineno}`;
      } else {
        return `${pathBasenameNoExt(entryWithLocation.source)}`;
      }
    }
  }
  return '';
};

export function formatTimeInSeconds(seconds: number) {
  if (seconds < 60) {
    return seconds.toFixed(1) + ' s';
  }

  var hours = Math.floor(seconds / 3600);
  var minutes = Math.floor((seconds % 3600) / 60);
  var remainingSeconds = seconds % 60;

  var formattedTime = '';
  if (hours > 0) {
    formattedTime += hours + ':';
    formattedTime += padZero(minutes) + ' hours';
  } else {
    formattedTime += padZero(minutes) + ':' + padZero(remainingSeconds) + ' min';
  }

  return formattedTime;
}

function padZero(n: number) {
  return n.toFixed(0).padStart(2, '0');
}

export function replaceNewLineChars(text: string) {
  return text.replace(/\n/g, '\\n').replace(/\r/g, '\\r');
}

export function formatArguments(
  entry: EntryMethodBase | EntryGenerator | EntryUntrackedGenerator,
): string {
  const args = entry.arguments;
  if (args !== undefined && args.length > 0) {
    let rep = [];
    for (const arg of args) {
      rep.push(replaceNewLineChars(`${arg.name}=${arg.value}`));
    }
    return rep.join(', ');
  }
  return '';
}

export const formatDuration = (entry: Entry) => {
  const asObj = <any>entry;
  const start: number | undefined = asObj.startDeltaInSeconds;
  if (start !== undefined && start >= 0) {
    const end: number | undefined = asObj.endDeltaInSeconds;
    if (end !== undefined && end >= 0) {
      const duration = end - start;
      return formatTimeInSeconds(duration);
    }
  }
  return '';
};

export function sanitizeHTML(html: string): string {
  let sanitize = DOMPurify.sanitize;
  if (!sanitize) {
    // It can be either in DOMPurify or DOMPurify.default.
    const d = DOMPurify as any;
    sanitize = d.default.sanitize;
  }
  const sanitizedHTML = sanitize(html);
  return sanitizedHTML;
}

export function extractDataFromImg(html: string): string | undefined {
  if (html.startsWith('<img ')) {
    const srcIndex = html.indexOf('src');
    if (srcIndex > 0) {
      const re = new RegExp('.*src\\s*=\\s*"(.*)".*');
      const result = re.exec(html);
      if (result !== undefined) {
        const dataSrc = result?.at(1);
        if (dataSrc && dataSrc.startsWith('data:')) {
          // Ok, we're dealing with an image.
          return dataSrc;
        }
      }
    }
  }
  return undefined;
}

export const IMG_HEIGHT_SMALL = 80;
export const IMG_MARGIN_SMALL = '5px';
export const HTML_HEIGHT_SMALL = 90;

export const getLogEntryHeight = (entry: Entry): number => {
  if (entry.type === Type.exception) {
    const excEntry = entry as EntryException;
    // Error entry height is dependent of the message line count
    return 32 + Math.min((excEntry.excMsg.split(/\r\n|\r|\n/).length - 1) * 16, 32);
  }
  if (entry.type === Type.log) {
    const logEntry = entry as EntryLog;
    if (logEntry.isHtml) {
      return HTML_HEIGHT_SMALL;
    }
    return 32 + Math.min((logEntry.message.split(/\r\n|\r|\n/).length - 1) * 16, 32);
  }
  if (entry.type === Type.console) {
    const entryConsole = entry as EntryConsole;
    // Console entry height is dependent of the message line count
    return 32 + Math.min((entryConsole.message.split(/\r\n|\r|\n/).length - 1) * 16, 32);
  }

  return 32;
};

export function pathBasenameNoExt(source: string): string {
  let basename = source;
  let index = Math.max(source.lastIndexOf('/'), source.lastIndexOf('\\'));
  if (index > 0) {
    basename = source.substring(index + 1);
  }
  index = basename.lastIndexOf('.');
  if (index > 0) {
    basename = basename.substring(0, index);
  }
  return basename;
}

export function logError(err: any | Error | undefined) {
  if (err !== undefined) {
    let indent = '    ';
    if (err.message) {
      console.log(indent + err.message);
    }
    if (err.stack) {
      let stack: string = '' + err.stack;
      console.log(stack.replace(/^/gm, indent));
    }
  }
}

export class Counter {
  private count: number;

  constructor(initial = 0) {
    this.count = initial;
  }

  public next(): number {
    return this.count++;
  }
}

export const isWindowDefined = () => {
  try {
    let x = window;
  } catch (error) {
    return false;
  }
  return true;
};

export const isDocumentDefined = () => {
  try {
    let x = document;
  } catch (error) {
    return false;
  }
  return true;
};

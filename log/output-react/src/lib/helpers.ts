import { FilteredEntries } from './logContext';
import {
  Entry,
  EntryConsole,
  EntryException,
  EntryGenerator,
  EntryLog,
  EntryMethodBase,
  EntryUntrackedGenerator,
  EntryWithLocationBase,
  Type,
} from './types';
import * as DOMPurify from 'dompurify';

export function entryDepth(entry: Entry) {
  return entry.id.split('-').length - 1;
}

export const leaveOnlyExpandedEntries = (
  data: Entry[],
  expandedItems: Set<string>,
): FilteredEntries => {
  // console.log('All: ', JSON.stringify(data));

  const entriesWithChildren: Set<string> = new Set();

  const ret: Entry[] = [];

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
    const depth = entryDepth(entry);
    const i = entry.id.lastIndexOf('-');
    if (i > 0) {
      const parentId = entry.id.substring(0, i);
      entriesWithChildren.add(parentId);
    }

    if (hideChildren) {
      if (depth > hideChildrenOnDepth) {
        // A child of the current entry we're hiding must be hidden.
        continue;
      }
      hideChildren = false;
    }

    ret.push(entry);

    if (!expandedItems.has(entry.id)) {
      // i.e.: the current item is hidden: hide it and all its children
      // until we get to the next sibling.
      // Note that the item itself is still shown, just children are hidden.
      hideChildren = true;
      hideChildrenOnDepth = depth;
    }
  }
  // console.log('Filtered: ', JSON.stringify(ret));
  return { entries: ret, entriesWithChildren };
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

  constructor() {
    this.count = 0;
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

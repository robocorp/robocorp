import { FilteredEntries } from './logContext';
import {
  Entry,
  EntryException,
  EntryGenerator,
  EntryMethod,
  EntryMethodBase,
  EntryUntrackedGenerator,
  Type,
} from './types';

const searchFn = (haystack: string, needle: string) =>
  haystack.toLowerCase().includes(needle.trim().toLowerCase());

function entryLevel(entry: Entry) {
  return entry.id.split('-').length - 1;
}

export const filterExpandedEntries = (
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
  let hideChildrenOnLevel: number = 0;

  for (const entry of data) {
    const level = entryLevel(entry);
    const i = entry.id.lastIndexOf('-');
    if (i > 0) {
      const parentId = entry.id.substring(0, i);
      entriesWithChildren.add(parentId);
    }

    if (hideChildren) {
      if (level > hideChildrenOnLevel) {
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
      hideChildrenOnLevel = level;
    }
  }
  // console.log('Filtered: ', JSON.stringify(ret));
  return { entries: ret, entriesWithChildren };
};

// TODO: Update location format
export const formatLocation = (entry: Entry) => {
  if (entry.source) {
    if (entry.lineno > 0) {
      return `${pathBasenameNoExt(entry.source)}:${entry.lineno}`;
    } else {
      return `${pathBasenameNoExt(entry.source)}`;
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

export function formatArguments(
  entry: EntryMethodBase | EntryGenerator | EntryUntrackedGenerator,
): string {
  const args = entry.arguments;
  if (args !== undefined && args.length > 0) {
    let rep = [];
    for (const arg of args) {
      rep.push(`${arg.name}=${arg.value}`);
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

export const getLogEntryHeight = (entry: Entry): number => {
  if (entry.type === Type.exception) {
    const excEntry = entry as EntryException;
    // Error entry height is dependent of the message line count
    return 32 + Math.min((excEntry.excMsg.split(/\r\n|\r|\n/).length - 1) * 16, 32);
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

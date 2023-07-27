import { getTitle } from '~/components/row/components/step/StepTitle';
import { entryDepth, leaveOnlyExpandedEntries } from './helpers';
import { FilteredEntries, IsExpanded } from './logContext';
import { Entry, Type, EntryLog, StatusLevel, ExpandInfo } from './types';
import { getValue } from '~/components/row/components/step/StepValue';
import { MutableRefObject } from 'react';

interface EntryAdded {
  entry: Entry;
  added: boolean;
  depth: number;
}

export const leaveOnlyFilteredExpandedEntries = (
  data: Entry[],
  isExpanded: IsExpanded,
  filter: string,
  lastExpandInfo: MutableRefObject<ExpandInfo>,
): FilteredEntries => {
  // When we have a filter we have to visit up to leafs to
  // determine if an entry is valid (because if a leaf
  // matches the parents must also be kept).
  const stack: EntryAdded[] = [];
  const filtered: Entry[] = [];
  let filterLower = filter.toLowerCase();

  for (const entry of data) {
    const depth = entryDepth(entry);
    if (stack.length === 0) {
      stack.push({ entry, added: false, depth });
    } else {
      while (stack.length > 0) {
        const last = stack.at(-1);
        if (last === undefined) {
          stack.pop();
          continue;
        }
        if (last.depth >= depth) {
          stack.pop();
          continue;
        }
        // Remove all the parents up to the current level.
        break;
      }
      stack.push({ entry, added: false, depth });
    }

    // At this point the stack should contain all the parents for the current
    // entry as well as the last entry as the last position. Now, decide whether
    // the entry should be kept or not. If it should be kept we have to add
    // all the parents which still weren't added as well as the item itself.
    let title = getTitle(entry);
    if (title !== undefined && title.length > 0 && title.toLowerCase().indexOf(filterLower) >= 0) {
      // matched
      for (const matchEntry of stack) {
        if (!matchEntry.added) {
          matchEntry.added = true;
          filtered.push(matchEntry.entry);
        }
      }
      continue; // No need to check value, we already matched.
    }

    // Need to check value because title didn't match.
    // Make an exception for random html (we can't really match it)
    let value = '';
    if (entry.type === Type.log) {
      const entryLog = entry as EntryLog;
      if (entryLog.isHtml) {
        switch (entryLog.status) {
          case StatusLevel.error:
            value = 'error';
            break;
          case StatusLevel.warn:
            value = 'warn';
            break;
          case StatusLevel.info:
            value = 'info';
            break;
          case StatusLevel.debug:
            value = 'debug';
            break;
        }
        if (value.length === 0) {
          continue;
        }
      }
    }
    if (value.length === 0) {
      const queried = getValue(entry);
      if (typeof queried === 'string') {
        value = queried;
      }
    }

    if (value.length > 0 && value.toLowerCase().indexOf(filterLower) >= 0) {
      // matched
      for (const matchEntry of stack) {
        if (!matchEntry.added) {
          matchEntry.added = true;
          filtered.push(matchEntry.entry);
        }
      }
    }
  }

  // console.log('Filtered: ', JSON.stringify(ret));
  return leaveOnlyExpandedEntries(filtered, isExpanded, lastExpandInfo);
};

import { getTitle } from '~/components/row/components/step/StepTitle';
import { entryDepth, getStatusLevel, leaveOnlyExpandedEntries } from './helpers';
import { FilteredEntries, IsExpanded } from './logContext';
import { Entry, Type, EntryLog, StatusLevel, ExpandInfo, TreeFilterInfo } from './types';
import { getValue } from '~/components/row/components/step/StepValue';
import { MutableRefObject } from 'react';

interface EntryAdded {
  entry: Entry;
  added: boolean;
  depth: number;
}

export const matchTreeFilterInfo = (entry: Entry, treeFilterInfo: TreeFilterInfo): boolean => {
  let statusLevel = getStatusLevel(entry);
  if (statusLevel === StatusLevel.unset) {
    return true;
  }
  if ((statusLevel & StatusLevel.success) !== 0) {
    // A 'regular' success is considered info.
    statusLevel |= StatusLevel.info;
  }
  // console.log(statusLevel);
  // if ((statusLevel & StatusLevel.debug) !== 0) {
  //   console.log('show debug');
  // }
  // if ((statusLevel & StatusLevel.info) !== 0) {
  //   console.log('show info');
  // }
  // if ((statusLevel & StatusLevel.warn) !== 0) {
  //   console.log('show warn');
  // }
  // if ((statusLevel & StatusLevel.error) !== 0) {
  //   console.log('show error');
  // }
  const accepted = (statusLevel & treeFilterInfo.showInTree) !== 0;
  // console.log('accepted', accepted, entry);
  return accepted;
};

export const matchFilterName = (entry: Entry, filter: string): boolean => {
  const filterLower = filter.toLocaleLowerCase();
  let title = getTitle(entry);
  if (title !== undefined && title.length > 0 && title.toLowerCase().indexOf(filterLower) >= 0) {
    return true;
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
        return false;
      }
    }
  }
  if (value.length === 0) {
    const queried = getValue(entry);
    if (typeof queried === 'string') {
      value = queried;
    }
  }

  return value.length > 0 && value.toLowerCase().indexOf(filterLower) >= 0;
};

export const leaveOnlyFilteredExpandedEntries = (
  data: Entry[],
  isExpanded: IsExpanded,
  lastExpandInfo: MutableRefObject<ExpandInfo>,
  treeFilterInfo: TreeFilterInfo,
): FilteredEntries => {
  let filtered: Entry[] = [];
  if (
    treeFilterInfo.showInTree ===
    (StatusLevel.debug | StatusLevel.info | StatusLevel.warn | StatusLevel.error)
  ) {
    // No filter is actually applied, just check for expand afterwards.
    filtered = data;
  } else {
    // When we have a filter we have to visit up to leafs to
    // determine if an entry is valid (because if a leaf
    // matches the parents must also be kept).
    const stack: EntryAdded[] = [];

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
      if (matchTreeFilterInfo(entry, treeFilterInfo)) {
        // matched
        for (const matchEntry of stack) {
          if (!matchEntry.added) {
            matchEntry.added = true;
            filtered.push(matchEntry.entry);
          }
        }
      }
    }
  }

  // console.log('Filtered: ', JSON.stringify(ret));
  return leaveOnlyExpandedEntries(filtered, isExpanded, lastExpandInfo);
};

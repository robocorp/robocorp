import { getTitle } from '~/components/row/components/step/StepTitle';
import { AnyIndexType, FocusIndexType, SearchInfoRequest, SelectionIndexType } from './logContext';
import { Entry, Type, EntryLog, StatusLevel, EntriesInfo } from './types';
import { getValue } from '~/components/row/components/step/StepValue';

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

function* parentIterator(
  inputString: string,
  separator: string = '-',
): Generator<string, void, unknown> {
  const parts = inputString.split(separator);

  for (let i = 0; i < parts.length - 1; i++) {
    yield parts.slice(0, parts.length - (i + 1)).join(separator);
  }
}

const getParentEntryIds = (entryId: string) => {
  const ret: string[] = [];
  for (const id of parentIterator(entryId)) {
    ret.push(id);
  }
  return ret;
};

function* circularArrayIterator<T>(
  arr: T[],
  foundAtIndex: number,
  direction: 'forward' | 'backward',
): Generator<T> {
  const length = arr.length;
  let currentIndex = foundAtIndex;
  if (direction == 'forward') {
    currentIndex++;
    if (currentIndex === length) {
      currentIndex = 0;
    }
  } else {
    currentIndex--;
    if (currentIndex < 0) {
      currentIndex = length - 1;
    }
  }
  let count = 0;

  while (count < length) {
    yield arr[currentIndex];
    if (direction === 'forward') {
      currentIndex++;
      if (currentIndex === length) {
        currentIndex = 0;
      }
    } else {
      currentIndex--;
      if (currentIndex === 0) {
        currentIndex = length - 1;
      }
    }
    count++;
  }
}

export interface SearchResult {
  expandParentIds: string[];
  selectedEntry: Entry;
}

export const makeSearch = (
  entriesInfo: EntriesInfo,
  searchInfoRequest: SearchInfoRequest,
  selectionIndex: SelectionIndexType,
  focusIndex: FocusIndexType,
): SearchResult | undefined => {
  if (searchInfoRequest.searchValue && searchInfoRequest.searchValue.length > 0) {
    let startAtIndex = 0;

    let useIndex: AnyIndexType = selectionIndex;
    if (!useIndex) {
      useIndex = focusIndex;
    } else {
      if (focusIndex) {
        // We have both. Use the one with the higher mtime.
        if (focusIndex.mtime > useIndex.mtime) {
          useIndex = focusIndex;
        }
      }
    }

    if (useIndex) {
      const focusedEntry = entriesInfo.allEntries[useIndex.indexAll];
      if (searchInfoRequest.incremental) {
        // we can still match the same entry
        if (matchFilterName(focusedEntry, searchInfoRequest.searchValue)) {
          const ret: string[] = getParentEntryIds(focusedEntry.id);
          return { expandParentIds: ret, selectedEntry: focusedEntry };
        }
      }

      // It didn't match or it wasn't an incremental search.
      // In this case we need to find the index in the filtered array
      // for the focused entry.

      for (let index = 0; index < entriesInfo.entriesWithFilterApplied.length; index++) {
        const element = entriesInfo.entriesWithFilterApplied[index];
        if (element.entryIndexAll === focusedEntry.entryIndexAll) {
          // Ok, we matched it
          startAtIndex = index;
          break;
        }
      }
    }

    // Now, do the actual search(starting at the given index)
    for (const element of circularArrayIterator(
      entriesInfo.entriesWithFilterApplied,
      startAtIndex,
      searchInfoRequest.direction,
    )) {
      if (element.id.indexOf('-hide(') !== -1) {
        continue;
      }
      if (matchFilterName(element, searchInfoRequest.searchValue)) {
        const ret: string[] = getParentEntryIds(element.id);
        return { expandParentIds: ret, selectedEntry: element };
      }
    }
  }

  return undefined;
};

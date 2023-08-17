import { Dispatch, MutableRefObject, SetStateAction } from 'react';
import { AnyIndexType, InvalidateTree } from './logContext';
import { getNextMtime, wasMtimeHandled } from './mtime';
import { EntriesInfo, Entry, InfoForScroll, getIndexInTree } from './types';
import { setScrollToChildrenOf, clearScrollToInfo } from './scroll';
import { IDChecker, entryDepth } from './helpers';

export const doesEntryMatchIndex = (entry: Entry, focusIndex: AnyIndexType): boolean => {
  if (focusIndex && focusIndex.indexAll === entry.entryIndexAll) {
    return true;
  }
  return false;
};

export const clearSelection = (
  selectionIndex: AnyIndexType,
  setSelectionIndex: React.Dispatch<React.SetStateAction<AnyIndexType>>,
) => {
  if (selectionIndex) {
    setSelectionIndex(null);
  }
};

export const setFocusIndexAndScroll = (
  setFocusIndex: React.Dispatch<React.SetStateAction<AnyIndexType>>,
  setScrollToItem: any,
  scrollInfo: any,
  entriesInfo: any,
  entry: Entry,
) => {
  setFocusIndex({
    indexAll: entry.entryIndexAll,
    mtime: getNextMtime(),
  });
  setScrollToItem(scrollInfo, entriesInfo, entry);
};

export const getChildrenIndexesInTree = (
  entriesInfo: EntriesInfo | undefined,
  parentId: string,
): number[] => {
  if (entriesInfo === undefined) {
    return [];
  }
  const indexes: number[] = [];
  const idChecker = new IDChecker(parentId);

  for (const entry of entriesInfo.treeEntries.entries) {
    const index = entriesInfo.treeEntries.idToEntryIndexInTreeArray.get(entry.id);
    if (index === undefined) {
      continue;
    }
    if (idChecker.isParentOf(entry.id)) {
      indexes.push(index);
    }
  }
  return indexes;
};

const updateSubtree = (
  curr: Set<string>,
  ids: string[],
  entriesInfo: EntriesInfo,
  forceMode: 'expandSubTree' | 'collapseSubTree',
): Set<string> | undefined => {
  let cp: Set<string> | undefined = new Set<string>(curr);
  let initialSize = cp.size;

  const expand = forceMode === 'expandSubTree';

  for (const id of ids) {
    const entry = entriesInfo.getEntryFromId(id);
    if (entry === undefined) {
      continue;
    }

    let indexInArray = entry.entryIndexAll;
    const allEntries = entriesInfo.allEntries;
    const initialDepth = entryDepth(entry);

    // Expand/collapse the initial one.
    if (expand) {
      cp.add(entry.id);
    } else {
      cp.delete(entry.id);
    }
    indexInArray++;

    // Expand/collapse all children.
    for (; indexInArray < allEntries.length; indexInArray++) {
      const entry = allEntries[indexInArray];
      const depth = entryDepth(entry);
      if (depth > initialDepth) {
        if (expand) {
          cp.add(entry.id);
        } else {
          cp.delete(entry.id);
        }
      } else {
        // We can stop as soon as we find an entry which is not a child
        // as it's guaranteed to be ordered.
        break;
      }
    }
  }
  if (cp.size === initialSize) {
    // Nothing changed, so, nothing needs to be updated.
    cp = undefined;
  }
  return cp;
};

/**
 * There are some restrictions in this function:
 *
 * If mode is toggle only one element may be passed.
 *
 * If more than one element is passed, scrollIntoView must be false.
 */
export const updateExpanded = (
  setExpandedEntries: Dispatch<SetStateAction<Set<string>>>,
  setInvalidateTree: Dispatch<SetStateAction<InvalidateTree>>,
  scrollInfo: MutableRefObject<InfoForScroll>,
  entriesInfo: EntriesInfo,
  ids: string[],
  forceMode: 'expand' | 'collapse' | 'toggle' | 'expandSubTree' | 'collapseSubTree',
  scrollIntoView: boolean,
): boolean => {
  let changedSomething = false;
  setExpandedEntries((curr: Set<string>) => {
    let cp = undefined;

    let entryWithLowestIndex: Entry | undefined = undefined;
    if (ids.length === 1) {
      entryWithLowestIndex = entriesInfo.getEntryFromId(ids[0]);
    }

    if (scrollIntoView) {
      if (ids.length !== 1) {
        // It could be done, but let's keep it simple untill we have the use case
        // (i.e.: compute the entryWithLowestIndex).
        throw new Error('To scroll into the view just one entry is supported.');
      }
    }

    if (forceMode === 'toggle') {
      if (ids.length !== 1) {
        throw new Error(
          'If forceMode is undefined for changing the expand state, only one entry may be passed.',
        );
      }
      const id = ids[0];

      // We always change it in toggle mode.
      cp = new Set<string>(curr);
      if (curr.has(id)) {
        cp.delete(id);
        forceMode = 'collapse';
      } else {
        cp.add(id);
        forceMode = 'expand';
      }
    } else if (forceMode === 'collapse') {
      for (const id of ids) {
        if (curr.has(id)) {
          if (cp === undefined) {
            cp = new Set<string>(curr);
          }
          cp.delete(id);
        }
      }
    } else if (forceMode === 'expand') {
      for (const id of ids) {
        if (!curr.has(id)) {
          if (cp === undefined) {
            cp = new Set<string>(curr);
          }
          cp.add(id);
        }
      }
    } else if (forceMode === 'expandSubTree') {
      cp = updateSubtree(curr, ids, entriesInfo, forceMode);
    } else if (forceMode === 'collapseSubTree') {
      cp = updateSubtree(curr, ids, entriesInfo, forceMode);
    }
    changedSomething = cp !== undefined;

    if (cp !== undefined) {
      if (scrollIntoView) {
        if (forceMode === 'expand' && entryWithLowestIndex) {
          setScrollToChildrenOf(scrollInfo, entriesInfo, entryWithLowestIndex.id);
        } else if (forceMode === 'collapse') {
          clearScrollToInfo(scrollInfo);
        }
      }

      if (entryWithLowestIndex) {
        const entry = entryWithLowestIndex;
        setInvalidateTree((prev: InvalidateTree) => {
          const curr = prev.indexInTreeEntries;
          let entryIndexInTree = getIndexInTree(entriesInfo, entry);
          if (entryIndexInTree === undefined) {
            // Unable to get it. Play safe and reset all.
            entryIndexInTree = 0;
          }
          if (curr < 0) {
            return {
              indexInTreeEntries: entryIndexInTree,
              mtime: getNextMtime(),
            };
          }
          if (!wasMtimeHandled('invalidateTree', prev.mtime)) {
            // The last one wasn't handled, we need to keep the lower value
            return {
              indexInTreeEntries: Math.min(entryIndexInTree, curr),
              mtime: getNextMtime(),
            };
          } else {
            return {
              indexInTreeEntries: entryIndexInTree,
              mtime: getNextMtime(),
            };
          }
        });
      } else {
        // It's not defined. Reset all entries.
        setInvalidateTree((prev: InvalidateTree) => {
          return {
            indexInTreeEntries: 0,
            mtime: getNextMtime(),
          };
        });
      }
      return cp;
    }
    return curr;
  });
  return changedSomething;
};

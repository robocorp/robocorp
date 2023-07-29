import { MutableRefObject } from 'react';
import { entryIdDepth } from './helpers';
import { EntriesInfo, Entry, InfoForScroll } from './types';
import { getNextMtime } from './mtime';

// Note: just setting the scroll won't do anything unless
// another operation is done along (such as updating the expanded
// state or selection) as the info lives in a mutable object
// usually untracked by react.
//
// The idea is that the information is set and then on the tree
// update it'll read it and do the scroll accordingly.

export const setScrollToChildrenOf = (
  scrollInfo: MutableRefObject<InfoForScroll>,
  entriesInfo: EntriesInfo,
  id: string,
) => {
  scrollInfo.current.mode = 'scrollToChildren';
  scrollInfo.current.scrollTargetId = id;
  scrollInfo.current.idDepth = entryIdDepth(id);
  scrollInfo.current.entriesInfo = entriesInfo;
  scrollInfo.current.mtime = getNextMtime();
};

export const setScrollToItem = (
  scrollInfo: MutableRefObject<InfoForScroll>,
  entriesInfo: EntriesInfo,
  entry: Entry,
) => {
  scrollInfo.current.mode = 'scrollToItem';
  scrollInfo.current.scrollTargetId = entry.id;
  scrollInfo.current.idDepth = entryIdDepth(entry.id);
  scrollInfo.current.entriesInfo = entriesInfo;
  scrollInfo.current.mtime = getNextMtime();
};

export const clearScrollToInfo = (scrollInfo: MutableRefObject<InfoForScroll>) => {
  scrollInfo.current.scrollTargetId = '';
  scrollInfo.current.idDepth = -1;
  scrollInfo.current.entriesInfo = undefined;
  scrollInfo.current.mtime = getNextMtime();
};

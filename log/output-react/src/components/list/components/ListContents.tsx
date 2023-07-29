import { FC, HTMLProps, useCallback, useEffect, useMemo, useRef } from 'react';
import { VariableSizeList } from 'react-window';
import { Box, useSize } from '@robocorp/components';
import { styled } from '@robocorp/theme';

import { RowCellsContainer } from '../../row/RowCellsContainer';
import { findMinAndMax, getLogEntryHeight, useLogContext } from '~/lib';
import { updateMtime } from '~/lib/mtime';
import { clearScrollToInfo } from '~/lib/scroll';
import { getChildrenIndexesInTree } from '~/lib/selections';
import { getIndexInTree } from '~/lib/types';

type Props = HTMLProps<HTMLDivElement>;

const Container = styled(Box)`
  height: calc(100% - ${({ theme }) => theme.sizes.$56});
  min-height: 0;
  overflow: hidden;
`;

export const ListContents: FC<Props> = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const listRef = useRef<VariableSizeList>(null);
  const { height } = useSize(containerRef);
  const { entriesInfo, invalidateTree, scrollInfo } = useLogContext();

  useEffect(() => {
    // This is needed when an item size changes. Note that in general when
    // we just append items, this isn't really needed, but if we change the
    // structure of the tree (when expanding or applying some filter)
    // it's needed because we change which item is appearing at a given
    // index.
    if (updateMtime('invalidateTree', invalidateTree.mtime)) {
      listRef.current?.resetAfterIndex(invalidateTree.indexInTreeEntries);
    }
    if (updateMtime('scroll', scrollInfo.current.mtime)) {
      if (scrollInfo.current.mode === 'scrollToChildren') {
        if (scrollInfo.current.scrollTargetId.length > 0) {
          const childrenIndexesInTree = getChildrenIndexesInTree(
            scrollInfo.current.entriesInfo,
            scrollInfo.current.scrollTargetId,
          );

          if (childrenIndexesInTree.length > 0) {
            const [minIndex, maxIndex] = findMinAndMax(childrenIndexesInTree);
            const diff = maxIndex - minIndex;
            if (diff > 5) {
              listRef.current?.scrollToItem(minIndex + 5);
            } else {
              listRef.current?.scrollToItem(maxIndex);
            }
          }
          clearScrollToInfo(scrollInfo);
        }
      } else if (scrollInfo.current.mode === 'scrollToItem') {
        const entriesInfo = scrollInfo.current.entriesInfo;
        const entry = entriesInfo?.getEntryFromId(scrollInfo.current.scrollTargetId);
        if (entriesInfo !== undefined && entry !== undefined) {
          const index = getIndexInTree(entriesInfo, entry);
          if (index !== undefined) {
            listRef.current?.scrollToItem(index);
          }
        }
        clearScrollToInfo(scrollInfo);
      }
    }
  }, [invalidateTree, scrollInfo.current.scrollTargetId]);

  const itemCount = useMemo(() => {
    return entriesInfo.treeEntries.entries.length;
  }, [entriesInfo.treeEntries]);

  const itemSize = useCallback(
    (itemIndex: number) => {
      const size = getLogEntryHeight(entriesInfo.treeEntries.entries[itemIndex]);
      return size;
    },
    [entriesInfo.treeEntries],
  );

  return (
    <Container ref={containerRef}>
      <VariableSizeList
        ref={listRef}
        height={height}
        width="100%"
        itemCount={itemCount}
        itemSize={itemSize}
        estimatedItemSize={32}
      >
        {RowCellsContainer}
      </VariableSizeList>
    </Container>
  );
};

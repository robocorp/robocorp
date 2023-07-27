import { FC, HTMLProps, useCallback, useEffect, useMemo, useRef } from 'react';
import { VariableSizeList } from 'react-window';
import { Box, useSize } from '@robocorp/components';
import { styled } from '@robocorp/theme';

import { RowCellsContainer } from '../../row/RowCellsContainer';
import { getLogEntryHeight, useLogContext } from '~/lib';
import { updateMtime } from '~/lib/mtime';

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
  const { filteredEntries, lastUpdatedIndexFiltered, lastExpandInfo } = useLogContext();

  useEffect(() => {
    // This is needed when an item size changes. Note that in general when
    // we just append items, this isn't really needed, but if we change the
    // structure of the tree (when expanding or applying some filter)
    // it's needed because we change which item is appearing at a given
    // index.
    if (updateMtime('lastUpdatedIndex', lastUpdatedIndexFiltered.mtime)) {
      listRef.current?.resetAfterIndex(lastUpdatedIndexFiltered.filteredIndex);
    }
    if (lastExpandInfo.current.lastExpandedId.length > 0) {
      const childrenIndexesFiltered = lastExpandInfo.current.childrenIndexesFiltered;
      if (childrenIndexesFiltered.size > 0) {
        let minIndex = -1;
        let maxIndex = -1;
        for (const entryIndex of childrenIndexesFiltered) {
          if (minIndex === -1) {
            minIndex = entryIndex;
            maxIndex = entryIndex;
          } else {
            if (entryIndex < minIndex) {
              minIndex = entryIndex;
            }
            if (entryIndex > maxIndex) {
              maxIndex = entryIndex;
            }
          }
        }
        const diff = maxIndex - minIndex;
        if (diff > 5) {
          listRef.current?.scrollToItem(minIndex + 5);
        } else {
          listRef.current?.scrollToItem(maxIndex);
        }
      }
      lastExpandInfo.current.lastExpandedId = '';
      lastExpandInfo.current.childrenIndexesFiltered = new Set();
    }
  }, [lastUpdatedIndexFiltered, lastExpandInfo.current.lastExpandedId]);

  const itemCount = useMemo(() => {
    return filteredEntries.entries.length;
  }, [filteredEntries]);

  const itemSize = useCallback(
    (itemIndex: number) => {
      const size = getLogEntryHeight(filteredEntries.entries[itemIndex]);
      return size;
    },
    [filteredEntries],
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

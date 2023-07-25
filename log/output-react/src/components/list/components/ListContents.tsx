import { FC, HTMLProps, useCallback, useEffect, useMemo, useRef } from 'react';
import { VariableSizeList } from 'react-window';
import { Box, useSize } from '@robocorp/components';
import { styled } from '@robocorp/theme';

import { RowCellsContainer } from '../../row/RowCellsContainer';
import { getLogEntryHeight, useLogContext } from '~/lib';

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
  const { filteredEntries, lastUpdatedIndex, lastExpandInfo } = useLogContext();

  useEffect(() => {
    // Per the docs, this isn't needed unless the item size changes (which shouldn't happen for us).
    // listRef.current?.resetAfterIndex(lastUpdatedIndex.current);
    if (lastExpandInfo.current.lastExpandedId.length > 0) {
      const childrenIndexes = lastExpandInfo.current.childrenIndexes;
      if (childrenIndexes.size > 0) {
        let minIndex = -1;
        let maxIndex = -1;
        for (const entryIndex of childrenIndexes) {
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
      lastExpandInfo.current.childrenIndexes = new Set();
    }
  });

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

import { FC, HTMLProps, useCallback, useMemo, useRef } from 'react';
import { VariableSizeList } from 'react-window';
import { Box, useSize } from '@robocorp/components';
import { styled } from '@robocorp/theme';

import { Row } from '~/components/row';
import { getLogEntryHeight, useLogContext } from '~/lib';

type Props = HTMLProps<HTMLDivElement>;

const Container = styled(Box)`
  height: calc(100% - ${({ theme }) => theme.sizes.$56});
  min-height: 0;
  overflow: hidden;
`;

export const Body: FC<Props> = () => {
  const { entries, lastUpdatedIndex } = useLogContext();
  const containerRef = useRef<HTMLDivElement>(null);
  const listRef = useRef<VariableSizeList>(null);
  const { height } = useSize(containerRef);

  const itemCount = useMemo(() => {
    listRef.current?.resetAfterIndex(lastUpdatedIndex.current);
    return entries.length;
  }, [entries]);

  const itemSize = useCallback(
    (itemIndex: number) => {
      const size = getLogEntryHeight(entries[itemIndex]);
      return size;
    },
    [entries],
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
        {Row}
      </VariableSizeList>
    </Container>
  );
};

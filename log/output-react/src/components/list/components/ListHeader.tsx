import type { FC, ReactNode } from 'react';
import { Box, componentWithRef, Typography } from '@robocorp/components';
import { styled } from '@robocorp/theme';
import { useLogContext } from '~/lib';

type Props = {
  children?: ReactNode;
  flex?: string;
};

// This is the element that contains the column titles.
const ColumnsTitleContainer = styled.div<{ mode: 'compact' | 'sparse' }>`
  padding: 0
    calc(
      ${({ theme, mode }) => (mode === 'compact' ? theme.space.$0 : theme.space.$12)} +
        var(--scrollbar-width)
    )
    0 ${({ theme, mode }) => (mode === 'compact' ? theme.space.$0 : theme.space.$24)};
  height: ${({ theme }) => theme.sizes.$48};
  display: flex;
  align-items: center;
  border-bottom: 1px solid ${({ theme }) => theme.colors.border.subtle.color};
`;

const Column: FC<Props> = ({ children, flex }) => {
  const { viewSettings } = useLogContext();
  const px = viewSettings.mode === 'compact' ? '$4' : '$8';
  return (
    <Box flex={flex}>
      <Typography
        variant="body.medium"
        fontWeight="medium"
        color="content.subtle"
        role="columnheader"
        as="div"
        px={px}
      >
        {children}
      </Typography>
    </Box>
  );
};

const compoundComponents = {
  Column,
};

export const ListHeader = componentWithRef<Props, HTMLDivElement, typeof compoundComponents>(
  ({ children, ...rest }, forwardedRef) => {
    const { viewSettings } = useLogContext();
    return (
      <ColumnsTitleContainer
        className="columnTitles"
        mode={viewSettings.mode}
        ref={forwardedRef}
        {...rest}
      >
        {children}
      </ColumnsTitleContainer>
    );
  },
  compoundComponents,
);

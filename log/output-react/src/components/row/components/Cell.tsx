import { FC, ReactNode } from 'react';
import { Box, Typography } from '@robocorp/components';
import { styled } from '@robocorp/theme';

type Props = {
  children?: ReactNode;
  minWidth: number;
  cellClass: string;
};

const Content = styled(Typography)`
  position: relative;
  line-height: ${({ theme }) => theme.space.$32};
`;

const StyledBox = styled(Box)`
  flex: 0 0 6rem;
  text-align: center;
`;

export const Cell: FC<Props> = ({ children, minWidth, cellClass }) => {
  return (
    <StyledBox minWidth={minWidth} className={cellClass}>
      <Content px="$8" variant="body.small" truncate={1}>
        {children}
      </Content>
    </StyledBox>
  );
};

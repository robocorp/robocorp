import { FC, ReactNode } from 'react';
import { Box, Typography } from '@robocorp/components';
import { styled } from '@robocorp/theme';

type Props = {
  children?: ReactNode;
};

const Content = styled(Typography)`
  position: relative;
  line-height: ${({ theme }) => theme.space.$32};
`;

export const Cell: FC<Props> = ({ children }) => {
  return (
    <Box flex="0 0 6rem" minWidth={0}>
      <Content px="$8" variant="body.small" truncate={1}>
        {children}
      </Content>
    </Box>
  );
};

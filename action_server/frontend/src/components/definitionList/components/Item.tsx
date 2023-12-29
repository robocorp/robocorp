import { FC, ReactNode } from 'react';
import { Box, Typography } from '@robocorp/components';
import { styled } from '@robocorp/theme';
import { IconType } from '@robocorp/icons';

type Props = {
  children?: ReactNode;
  /**
   * Icon appended after content
   */
  iconAfter?: IconType;
};

const Container = styled.div`
  display: flex;
  align-items: flex-start;
  padding: ${({ theme }) => theme.space.$8} ${({ theme }) => theme.space.$16};
  word-break: break-all;
  font-weight: ${({ theme }) => theme.fontWeights.medium};

  > a {
    font-weight: ${({ theme }) => theme.fontWeights.medium};
  }
`;

const KeyContainer = styled(Container)`
  color: ${({ theme }) => theme.color('content.subtle.light')};
`;

export const DefinitionListKey: FC<Props> = ({ children, iconAfter: IconAfter }) => (
  <KeyContainer>
    <Box display="flex" alignItems="center" gap="$8">
      <Typography fontWeight="medium">{children}</Typography>
      {IconAfter ? <IconAfter color="content.subtle.light" /> : null}
    </Box>
  </KeyContainer>
);

export const DefinitionListValue: FC<Omit<Props, 'iconAfter'>> = ({ children }) => (
  <Container>{children}</Container>
);

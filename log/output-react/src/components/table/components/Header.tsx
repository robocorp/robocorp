import type { FC, ReactNode } from 'react';
import { Box, componentWithRef, Typography } from '@robocorp/components';
import { styled } from '@robocorp/theme';

type Props = {
  children?: ReactNode;
  flex?: string;
};

const Container = styled.div`
  padding: 0 calc(${({ theme }) => theme.space.$12} + var(--scrollbar-width)) 0
    ${({ theme }) => theme.space.$24};
  height: ${({ theme }) => theme.sizes.$48};
  display: flex;
  align-items: center;
  border-bottom: 1px solid ${({ theme }) => theme.colors.border.subtle.color};
`;

const Column: FC<Props> = ({ children, flex }) => {
  return (
    <Box flex={flex}>
      <Typography
        variant="body.medium"
        fontWeight="medium"
        color="content.subtle"
        role="columnheader"
        as="div"
        px="$8"
      >
        {children}
      </Typography>
    </Box>
  );
};

const compoundComponents = {
  Column,
};

export const Header = componentWithRef<Props, HTMLDivElement, typeof compoundComponents>(
  ({ children, ...rest }, forwardedRef) => {
    return (
      <Container ref={forwardedRef} {...rest}>
        {children}
      </Container>
    );
  },
  compoundComponents,
);

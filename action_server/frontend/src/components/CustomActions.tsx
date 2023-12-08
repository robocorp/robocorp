import { FC, ReactNode, useContext } from 'react';
import { variant as variants } from 'styled-system';
import { styled } from '@robocorp/theme';

import { createContext } from 'react';
import { Button } from '@robocorp/components';

export type HeaderSize = 'x-large' | 'x2-large' | 'large' | 'medium' | 'small';

export const HeaderContext = createContext<{
  size: HeaderSize;
}>({
  size: 'large',
});

type Props = {
  children?: ReactNode;
};

const Container = styled.div<{ $size: HeaderSize }>`
  grid-area: actions;

  ${({ theme }) => theme.screen.m} {
    ${({ theme }) =>
      variants({
        prop: '$size',
        variants: {
          small: {
            marginBottom: theme.sizes.$12,
            [theme.screen.m]: {
              marginTop: theme.space.$12,
            },
          },
          medium: {
            marginBottom: theme.sizes.$12,
            [theme.screen.m]: {
              marginTop: theme.space.$12,
            },
          },
          large: {
            marginBottom: theme.sizes.$16,
          },
          'x-large': {
            marginBottom: theme.space.$24,
          },
        },
      })}
  }
`;

/**
 * Header component helper component to display  screen related actions
 *
 * @see
 * {@link https://design-system.robocorp.com/component/header}
 */

// This is mostly the same thing as Header.Actions, but with collapse always false.
// This is mostly the same thing as Header.Actions, but with collapse always false.
// This is mostly the same thing as Header.Actions, but with collapse always false.
// This is mostly the same thing as Header.Actions, but with collapse always false.
// This is mostly the same thing as Header.Actions, but with collapse always false.
export const CustomActions: FC<Props> = ({ children }) => {
  const { size } = useContext(HeaderContext);

  const collapse = false;

  return (
    <Container $size={size}>
      <Button.Group size="medium" align="right" collapse={collapse}>
        {children}
      </Button.Group>
    </Container>
  );
};

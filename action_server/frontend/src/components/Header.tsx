import { FC, useCallback } from 'react';
import { Box, Button } from '@robocorp/components';
import { styled } from '@robocorp/theme';
import { IconMenu, IconSun } from '@robocorp/icons/iconic';
import { useActionServerContext } from '~/lib/actionServerContext';

const StyledTopNavigationButton = styled(Button)`
  display: none;

  ${({ theme }) => theme.screen.m} {
    display: block;
  }
`;

type Props = { onClickMenuButton: () => void };

export const HeaderAndMenu: FC<Props> = ({ onClickMenuButton }) => {
  const { setViewSettings } = useActionServerContext();

  const onToggleTheme = useCallback(() => {
    setViewSettings((curr) => ({
      ...curr,
      theme: curr.theme === 'dark' ? 'light' : 'dark',
    }));
  }, []);

  return (
    <Box display="flex" height={84} alignItems="center" px="$12" justifyContent="flex-end">
      <StyledTopNavigationButton
        aria-label="toggleMainMenu"
        variant="ghost"
        icon={IconMenu}
        onClick={onClickMenuButton}
      />
      <Box ml={['$16', '$16', '$8']}>
        <Button
          className="desktop theme-switch"
          aria-label="Toggle theme"
          onClick={onToggleTheme}
          icon={IconSun}
          variant="ghost"
        />
      </Box>
    </Box>
  );
};

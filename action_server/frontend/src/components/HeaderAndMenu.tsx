import { FC, useCallback } from 'react';
import { Box, Button, Header as BaseHeader, Menu, Header, Link } from '@robocorp/components';

import { IconSettings } from '@robocorp/icons';
import { useActionServerContext } from '~/lib/actionServerContext';
import { useNavigate } from 'react-router-dom';

type Props = {};
export const HeaderAndMenu: FC<Props> = () => {
  let px = '$24';
  let pt = '$32';

  const { viewSettings, setViewSettings } = useActionServerContext();

  const onToggleTheme = useCallback(() => {
    setViewSettings((curr) => ({
      ...curr,
      theme: curr.theme === 'dark' ? 'light' : 'dark',
    }));
  }, []);

  const navigate = useNavigate();

  return (
    <Box px={px} pt={pt} pb="0" backgroundColor="background.primary" id="base-header">
      <BaseHeader className="base-header-container" size="medium">
        <BaseHeader.Title
          title={
            <Link
              onClick={() => {
                navigate('/');
              }}
            >
              Robocorp Action Server
            </Link>
          }
        ></BaseHeader.Title>
        <Header.Actions>
          <Menu
            trigger={
              <Button
                icon={IconSettings}
                variant="secondary"
                aria-label="Settings"
                title="Settings (theme, layout, columns)"
              />
            }
            leaveMenuOpenOnItemSelect
          >
            <Menu.Title>Theme</Menu.Title>
            <Menu.Checkbox checked={viewSettings.theme === 'dark'} onClick={onToggleTheme}>
              Dark
            </Menu.Checkbox>
            <Menu.Checkbox checked={viewSettings.theme === 'light'} onClick={onToggleTheme}>
              Light
            </Menu.Checkbox>
          </Menu>
        </Header.Actions>
      </BaseHeader>
    </Box>
  );
};

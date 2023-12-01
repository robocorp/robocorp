import { SideNavigation, Menu, Box, Link } from '@robocorp/components';
import { IconActivity } from '@robocorp/icons';
import { FC, StrictMode, useCallback, useEffect, useMemo, useState } from 'react';
import { ThemeProvider, styled } from '@robocorp/theme';
import { IconLogoRobocorp } from '@robocorp/icons/logos';
import {
  ActionServerContext,
  ActionServerContextType,
  ViewSettings,
  defaultActionServerState,
  defaultTheme,
} from '../lib/actionServerContext';
import { HeaderAndMenu } from './HeaderAndMenu';
import { Outlet, RouterProvider, createBrowserRouter, useNavigate } from 'react-router-dom';
import { ActionPackages } from './ActionPackages';
import { ActionRuns } from './ActionRuns';
import { LoadedActions, LoadedRuns } from '~/lib/types';
import { refreshActions, refreshRuns } from '~/lib/requestData';
import { Welcome } from './Welcome';

const Main = styled.main<{ isCollapsed: boolean }>`
  background: ${({ theme }) => theme.colors.background.primary.color};
  height: 100%;
  display: grid;
  grid-template-columns: ${({ isCollapsed }) => (isCollapsed ? 0 : 240)}px 1fr;
  grid-template-rows: auto 1fr;
  grid-template-areas: 'aside header' 'aside section';
  ${({ theme }) => theme.screen.m} {
    grid-template-columns: 1fr;
    grid-template-areas: 'header' 'section';
  }

  > header {
    grid-area: header;
  }

  > section {
    grid-area: section;
    padding: 2px calc(5rem - var(--scrollbar-width)) 3rem 5rem;

    ${({ theme }) => theme.screen.m} {
      padding: 0 ${({ theme }) => theme.space.$32};
    }

    ${({ theme }) => theme.screen.s} {
      padding: 0 ${({ theme }) => theme.space.$16};
    }
  }
`;

function ErrorPage() {
  const navigate = useNavigate();
  return (
    <div>
      <h4>Error: no content found at this url...</h4>
      <p>
        <br />
        <Link
          onClick={() => {
            navigate('/');
          }}
        >
          Navigate back to the Robocorp Action Server root url.
        </Link>
      </p>
    </div>
  );
}

const Root = () => {
  const [viewSettings, setViewSettings] = useState<ViewSettings>(
    defaultActionServerState.viewSettings,
  );
  const [loadedRuns, setLoadedRuns] = useState<LoadedRuns>(defaultActionServerState.loadedRuns);
  const [loadedActions, setLoadedActions] = useState<LoadedActions>(defaultActionServerState.loadedActions);

  const ctx: ActionServerContextType = { viewSettings, setViewSettings, loadedRuns, setLoadedRuns, loadedActions, setLoadedActions };

  const actionServerContextValue = useMemo(
    () => ctx,
    [viewSettings, setViewSettings, loadedRuns, setLoadedRuns, loadedActions, setLoadedActions],
  );
  const [isCollapsed, setIsCollapsed] = useState<boolean>(false);
  const onClose = useCallback(() => setIsCollapsed(false), []);

  const navigate = useNavigate();

  return (
    <ThemeProvider name={viewSettings.theme}>
      <ActionServerContext.Provider value={actionServerContextValue}>
        <HeaderAndMenu />
        <Main isCollapsed={isCollapsed}>
          <SideNavigation aria-label="Navigation" open={isCollapsed} onClose={onClose}>
            <Menu.Item
              icon={<IconActivity size="small" />}
              onClick={() => {
                refreshActions(loadedActions, setLoadedActions);
                navigate('/actions');
              }}
            >
              Action Packages
            </Menu.Item>
            <Menu.Item
              icon={<IconActivity size="small" />}
              onClick={() => {
                refreshRuns(loadedRuns, setLoadedRuns);
                navigate('/runs');
              }}
            >
              Action Runs
            </Menu.Item>
            <Box display="flex" alignItems="center" ml={24} mt={8} color="content.subtle.light">
              <IconLogoRobocorp size={24} />
              <Box ml={8} fontSize={12}>
                Powered by Robocorp
              </Box>
            </Box>
          </SideNavigation>
          <Outlet />
        </Main>
      </ActionServerContext.Provider>
    </ThemeProvider>
  );
};

export const ActionServer = () => {
  const router = createBrowserRouter([
    {
      path: '/',
      element: <Root />,
      errorElement: <ErrorPage />,
      children: [
        {
          path: '',
          element: <Welcome />,
        },
        {
          path: 'actions',
          element: <ActionPackages />,
        },
        {
          path: 'runs',
          element: <ActionRuns />,
        },
        {
          path: '*',
          element: <ErrorPage />,
        },
      ],
    },
  ]);

  return (
    <StrictMode>
      <RouterProvider router={router} />
    </StrictMode>
  );
};

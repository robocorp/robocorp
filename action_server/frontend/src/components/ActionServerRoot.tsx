import { SideNavigation, Menu, Box, Link } from '@robocorp/components';
import { IconActivity } from '@robocorp/icons';
import { StrictMode, useCallback, useEffect, useMemo, useState } from 'react';
import { ThemeProvider, styled } from '@robocorp/theme';
import { IconLogoRobocorp } from '@robocorp/icons/logos';
import {
  ActionServerContext,
  ActionServerContextType,
  ViewSettings,
  defaultActionServerState,
} from '../lib/actionServerContext';
import { HeaderAndMenu } from './HeaderAndMenu';
import { Outlet, RouterProvider, createBrowserRouter, useNavigate } from 'react-router-dom';
import { ActionPackages } from './ActionPackages';
import { ActionRuns } from './ActionRuns';
import { LoadedActionsPackages, LoadedRuns } from '~/lib/types';
import { Welcome } from './Welcome';
import { ActionRunConsole, actionRunConsoleLoader } from './ActionRunConsole';
import { ActionRunLog, actionRunLogLoader } from './ActionRunLog';
import {
  startTrackActions,
  startTrackRuns,
  stopTrackActions,
  stopTrackRuns,
} from '~/lib/requestData';

const Main = styled.main<{ isCollapsed: boolean }>`
  background: ${({ theme }) => theme.colors.background.primary.color};
  /*height: 100%;*/
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
  const [loadedActions, setLoadedActions] = useState<LoadedActionsPackages>(
    defaultActionServerState.loadedActions,
  );

  const ctx: ActionServerContextType = {
    viewSettings,
    setViewSettings,
    loadedRuns,
    setLoadedRuns,
    loadedActions,
    setLoadedActions,
  };

  const actionServerContextValue = useMemo(
    () => ctx,
    [viewSettings, setViewSettings, loadedRuns, setLoadedRuns, loadedActions, setLoadedActions],
  );
  const [showNavInSmallMode, setNavInSmallMode] = useState<boolean>(false);
  const onClose = useCallback(() => setNavInSmallMode(false), []);
  const onClickMenuButton = useCallback(() => setNavInSmallMode(true), []);

  const navigate = useNavigate();
  useEffect(() => {
    startTrackActions(setLoadedActions);
    startTrackRuns(setLoadedRuns);

    return () => {
      stopTrackActions(setLoadedActions);
      stopTrackRuns(setLoadedRuns);
    };
  }, []);

  return (
    <ThemeProvider name={viewSettings.theme}>
      <ActionServerContext.Provider value={actionServerContextValue}>
        <HeaderAndMenu onClickMenuButton={onClickMenuButton} />
        <Main isCollapsed={false}>
          <SideNavigation aria-label="Navigation" open={showNavInSmallMode} onClose={onClose}>
            {/* 
            Hack so that the X button to close is properly shown. 
            Otherwise the menu appears on top of it.
            */}
            {showNavInSmallMode ? <div style={{ height: '3em' }} /> : <></>}
            {showNavInSmallMode ? (
              <Menu.Item
                icon={<IconActivity size="small" />}
                onClick={() => {
                  navigate('/');
                  onClose();
                }}
              >
                Main
              </Menu.Item>
            ) : (
              <></>
            )}
            <Menu.Item
              icon={<IconActivity size="small" />}
              onClick={() => {
                navigate('/actions');
                onClose();
              }}
            >
              Action Packages
            </Menu.Item>
            <Menu.Item
              icon={<IconActivity size="small" />}
              onClick={() => {
                navigate('/runs');
                onClose();
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

export const ActionServerRoot = () => {
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
          path: 'runs/:id/console',
          element: <ActionRunConsole />,
          loader: actionRunConsoleLoader,
        },
        {
          path: '*',
          element: <ErrorPage />,
        },
      ],
    },
    {
      path: 'runs/:id/log.html',
      element: <ActionRunLog />,
      loader: actionRunLogLoader,
    },
  ]);

  // Note: strict mode makes rendering twice, so, beware of duplicate network requests
  // due to the additional mount/unmount.
  return (
    <StrictMode>
      <RouterProvider router={router} />
    </StrictMode>
  );
};

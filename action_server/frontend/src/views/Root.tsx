import {
  SideNavigation,
  Box,
  Link,
  Scroll,
  useSystemTheme,
  Typography,
} from '@robocorp/components';
import { StrictMode, useCallback, useEffect, useMemo, useState } from 'react';
import { ThemeOverrides, ThemeProvider, styled } from '@robocorp/theme';
import { IconBolt, IconUnorderedList } from '@robocorp/icons/iconic';
import { IconLogoRobocorp } from '@robocorp/icons/logos';
import { Outlet, RouterProvider, createBrowserRouter, useLocation } from 'react-router-dom';

import { HeaderAndMenu } from '~/components/Header';
import { ActionServerLogo, Redirect } from '~/components';
import { LoadedActionsPackages, LoadedRuns } from '~/lib/types';
import {
  startTrackActions,
  startTrackRuns,
  stopTrackActions,
  stopTrackRuns,
} from '~/lib/requestData';
import { useLocalStorage } from '~/lib/useLocalStorage';

import { ActionRuns } from './runs';
import { ActionPackages } from './actions';
import {
  ActionServerContext,
  ActionServerContextType,
  ViewSettings,
  defaultActionServerState,
} from '../lib/actionServerContext';

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

  > aside {
    grid-area: aside;
  }

  > section {
    grid-area: section;
    padding: 0 calc(5rem - var(--scrollbar-width)) 3rem 5rem;

    ${({ theme }) => theme.screen.m} {
      padding: 0 ${({ theme }) => theme.space.$32};
    }

    ${({ theme }) => theme.screen.s} {
      padding: 0 ${({ theme }) => theme.space.$16};
    }
  }
`;

const overrides: ThemeOverrides = {
  fonts: {
    title:
      '-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif,Apple Color Emoji,Segoe UI Emoji,Segoe UI Symbol',
    default:
      '-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif,Apple Color Emoji,Segoe UI Emoji,Segoe UI Symbol',
  },
};

const ContentScroll = styled(Scroll)`
  min-height: 0px;

  > div {
    padding: 0 ${({ theme }) => theme.space.$8};
    border-radius: ${({ theme }) => theme.radii.$8};
  }
`;

const ErrorPage = () => {
  return (
    <div>
      <h4>Error: no content found at this url...</h4>
      <p>
        <br />
        <Link href="/">Navigate back to the Robocorp Action Server root url.</Link>
      </p>
    </div>
  );
};

const Root = () => {
  const location = useLocation();
  const systemTheme = useSystemTheme();
  const [viewSettings, setViewSettings] = useLocalStorage<ViewSettings>('view-settings', {
    theme: systemTheme,
  });
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

  useEffect(() => {
    startTrackActions(setLoadedActions);
    startTrackRuns(setLoadedRuns);

    return () => {
      stopTrackActions(setLoadedActions);
      stopTrackRuns(setLoadedRuns);
    };
  }, []);

  return (
    <ThemeProvider name={viewSettings.theme} overrides={overrides}>
      <ActionServerContext.Provider value={actionServerContextValue}>
        <Main isCollapsed={false}>
          <HeaderAndMenu onClickMenuButton={onClickMenuButton} />
          <SideNavigation aria-label="Navigation" open={showNavInSmallMode} onClose={onClose}>
            <Box display="flex" alignItems="center" gap="$8" height="$32" mb="$48" px="$8">
              <Box
                display="flex"
                borderRadius="$8"
                width="$32"
                height="$32"
                backgroundColor="blue70"
                alignItems="center"
                justifyContent="center"
              >
                <ActionServerLogo size={20} />
              </Box>
              <Typography fontWeight={600}>Action Server</Typography>
            </Box>
            <ContentScroll>
              <SideNavigation.Link
                aria-current={location.pathname.startsWith('/actions')}
                href="/actions"
                icon={<IconBolt />}
              >
                Actions
              </SideNavigation.Link>
              <SideNavigation.Link
                aria-current={location.pathname.startsWith('/runs')}
                href="/runs"
                icon={<IconUnorderedList />}
              >
                Runs
              </SideNavigation.Link>
            </ContentScroll>

            <Box display="flex" alignItems="center" ml={24} mt={8} color="content.subtle.light">
              <IconLogoRobocorp size={24} />
              <Box ml={8} fontSize={12}>
                Powered by Robocorp
              </Box>
            </Box>
          </SideNavigation>
          <section>
            <Outlet />
          </section>
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
          element: <Redirect path="/actions" />,
        },
        {
          path: '/actions/:actionId?',
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

  // Note: strict mode makes rendering twice, so, beware of duplicate network requests
  // due to the additional mount/unmount.
  return (
    <StrictMode>
      <RouterProvider router={router} />
    </StrictMode>
  );
};

import { SideNavigation, Menu } from '@robocorp/components';
import { IconActivity } from '@robocorp/icons';
import { useMemo, useState } from 'react';
import { ThemeProvider, styled } from '@robocorp/theme';
import {
  ActionServerContext,
  ActionServerContextType,
  ViewSettings,
  defaultTheme,
} from '../lib/actionServerContext';

const Main = styled.main`
  display: grid;
  grid-auto-columns: 1fr;
  grid-template-rows: auto minmax(0, 1fr);
  height: 100vh;
`;

export const ActionServer = () => {
  const [open, setOpen] = useState<boolean>(false);
  const [input, setInput] = useState<string>('');

  const [viewSettings, setViewSettings] = useState<ViewSettings>({ theme: defaultTheme });
  const ctx: ActionServerContextType = { viewSettings, setViewSettings };

  const actionServerContextValue = useMemo(() => ctx, [viewSettings, setViewSettings]);

  return (
    <ThemeProvider name={viewSettings.theme}>
      <Main>
        <ActionServerContext.Provider value={actionServerContextValue}>
          <SideNavigation
            aria-label="Navigation"
            open={true}
            onClose={() => setOpen(false)}
          ></SideNavigation>
        </ActionServerContext.Provider>
      </Main>
    </ThemeProvider>
  );
};

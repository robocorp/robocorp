import { useCallback, useMemo, useState } from 'react';
import { ThemeProvider, styled } from '@robocorp/theme';

import { Header, Details, Table } from '~/components';
import { LogContext, dummyData, filterEntries, defaultLogState } from '~/lib';
import { ViewSettings } from './lib/types';

const Main = styled.main`
  display: grid;
  grid-auto-columns: 1fr;
  grid-template-rows: auto minmax(0, 1fr);
  height: 100vh;
`;

export const Log = () => {
  const [filter, setFilter] = useState('');
  const [expandedEntries, setExpandedEntries] = useState<string[]>([]);
  const [activeIndex, setActiveIndex] = useState<number | null>(null);
  const [viewSettings, setViewSettings] = useState<ViewSettings>(defaultLogState.viewSettings);

  const toggleEntry = useCallback((id: string) => {
    setExpandedEntries((curr) =>
      curr.indexOf(id) > -1
        ? curr.filter((value) => value !== id && value.indexOf(`${id}-`) !== 0)
        : [...curr, id],
    );
  }, []);

  const entries = useMemo(() => {
    return filterEntries(dummyData(), filter, expandedEntries);
  }, [expandedEntries, filter]);

  const logContextValue = useMemo(
    () => ({
      entries,
      activeIndex,
      setActiveIndex,
      expandedEntries,
      toggleEntry,
      viewSettings,
      setViewSettings,
    }),
    [activeIndex, entries, viewSettings],
  );

  return (
    <ThemeProvider name="light">
      <Main>
        <LogContext.Provider value={logContextValue}>
          <Header filter={filter} setFilter={setFilter} />
          <Table />
          <Details />
        </LogContext.Provider>
      </Main>
    </ThemeProvider>
  );
};

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { ThemeProvider, styled } from '@robocorp/theme';
import { Header, Details, Table } from '~/components';
import { LogContext, filterEntries, defaultLogState } from '~/lib';
import { Entry, ViewSettings } from './lib/types';
import { reactCallSetAllEntriesCallback } from './treebuild/effectCallbacks';

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
  const [entries, setEntries] = useState<Entry[]>([]); // Start empty. Entries will be added as they're found.
  const lastUpdatedIndex = useRef<number>(0);

  /**
   * Register callback which should be used to set entries.
   */
  useEffect(() => {
    reactCallSetAllEntriesCallback((newEntries: Entry[], updatedFromIndex = 0) => {
      setEntries(() => {
        lastUpdatedIndex.current = updatedFromIndex;
        return [...newEntries];
      });
    });
  }, []);

  /**
   * Filter entries by current filter and expanded entries
   */
  const filteredEntries = useMemo(() => {
    return filterEntries(entries, filter, expandedEntries);
  }, [entries, expandedEntries, filter]);

  /**
   * Single entry expansion toggle callacbk
   */
  const toggleEntry = useCallback((id: string) => {
    lastUpdatedIndex.current = 0;
    setExpandedEntries((curr) =>
      curr.indexOf(id) > -1
        ? curr.filter((value) => value !== id && value.indexOf(`${id}-`) !== 0)
        : [...curr, id],
    );
  }, []);

  const logContextValue = useMemo(
    () => ({
      entries: filteredEntries,
      activeIndex,
      setActiveIndex,
      expandedEntries,
      toggleEntry,
      viewSettings,
      setViewSettings,
      lastUpdatedIndex,
    }),
    [activeIndex, filteredEntries, viewSettings],
  );

  return (
    <ThemeProvider name={viewSettings.theme}>
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

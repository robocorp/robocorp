import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { ThemeProvider, styled } from '@robocorp/theme';
import { Header, Details, Table } from './components';
import {
  LogContext,
  leaveOnlyExpandedEntries,
  defaultLogState,
  LogContextType,
  RunInfo,
  createDefaultRunInfo,
} from '~/lib';
import { Entry, ViewSettings } from './lib/types';
import {
  reactCallSetAllEntriesCallback,
  reactCallSetRunInfoCallback,
} from './treebuild/effectCallbacks';
import { leaveOnlyFilteredExpandedEntries } from './lib/filteringHelpers';

const Main = styled.main`
  display: grid;
  grid-auto-columns: 1fr;
  grid-template-rows: auto minmax(0, 1fr);
  height: 100vh;
`;

export const Log = () => {
  const [filter, setFilter] = useState('');
  const [expandedEntries, setExpandedEntries] = useState<Set<string>>(new Set<string>());
  const [activeIndex, setActiveIndex] = useState<number | null | 'information'>(null);
  const [runInfo, setRunInfo] = useState<RunInfo>(createDefaultRunInfo());
  const [viewSettings, setViewSettings] = useState<ViewSettings>(defaultLogState.viewSettings);
  const [entries, setEntries] = useState<Entry[]>([]); // Start empty. Entries will be added as they're found.
  const lastUpdatedIndex = useRef<number>(0);

  /**
   * Register callback which should be used to set entries.
   */
  useEffect(() => {
    reactCallSetAllEntriesCallback(
      (newEntries: Entry[], newExpanded: string[], updatedFromIndex = 0) => {
        if (newExpanded.length > 0) {
          setExpandedEntries((curr) => {
            const set = new Set<string>(curr);
            for (const s of newExpanded) {
              set.add(s);
            }
            return set;
          });
        }

        setEntries(() => {
          // console.log('Set entries to: ' + JSON.stringify(newEntries));
          lastUpdatedIndex.current = updatedFromIndex;
          return [...newEntries];
        });

        return undefined;
      },
    );

    reactCallSetRunInfoCallback((runInfo: RunInfo) => {
      setRunInfo(() => {
        return runInfo;
      });
    });
  }, []);

  // Toggle the expanded state.
  const toggleEntry = useCallback((id: string) => {
    lastUpdatedIndex.current = 0;
    setExpandedEntries((curr) => {
      const cp = new Set<string>(curr);

      if (curr.has(id)) {
        cp.delete(id);
      } else {
        cp.add(id);
      }
      return cp;
    });
  }, []);

  // Leave only items which are actually expanded.
  const filteredEntries = useMemo(() => {
    if (filter !== undefined && filter.length > 0) {
      return leaveOnlyFilteredExpandedEntries(entries, expandedEntries, filter);
    }
    return leaveOnlyExpandedEntries(entries, expandedEntries);
  }, [entries, expandedEntries, filter]);

  const ctx: LogContextType = {
    expandedEntries,
    filteredEntries,
    toggleEntry,
    activeIndex,
    setActiveIndex,
    viewSettings,
    setViewSettings,
    runInfo,
    lastUpdatedIndex,
  };

  const logContextValue = useMemo(
    () => ctx,
    [activeIndex, expandedEntries, filteredEntries, viewSettings],
  );

  return (
    <ThemeProvider name={viewSettings.theme}>
      <Main>
        <LogContext.Provider value={logContextValue}>
          <Header filter={filter} setFilter={setFilter} runInfo={runInfo} />
          <Table />
          <Details />
        </LogContext.Provider>
      </Main>
    </ThemeProvider>
  );
};

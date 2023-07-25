import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { ThemeProvider, styled } from '@robocorp/theme';
import {
  LogContext,
  leaveOnlyExpandedEntries,
  defaultLogState,
  LogContextType,
  RunInfo,
  createDefaultRunInfo,
  RunIdsAndLabel,
  createDefaultRunIdsAndLabel,
  entryIdDepth,
} from '~/lib';
import { Entry, ExpandInfo, ViewSettings } from './lib/types';
import {
  reactCallSetAllEntriesCallback,
  reactCallSetRunIdsAndLabelCallback,
  reactCallSetRunInfoCallback,
} from './treebuild/effectCallbacks';
import { leaveOnlyFilteredExpandedEntries } from './lib/filteringHelpers';
import { Details } from './components/details/Details';
import { HeaderAndMenu } from './components/header/HeaderAndMenu';
import { ListHeaderAndContents } from './components/list/ListHeaderAndContents';

const Main = styled.main`
  display: grid;
  grid-auto-columns: 1fr;
  grid-template-rows: auto minmax(0, 1fr);
  height: 100vh;
`;

export const Log = () => {
  const [filter, setFilter] = useState('');
  const [expandedEntries, setExpandedEntries] = useState<Set<string>>(new Set<string>());
  const [activeIndex, setActiveIndex] = useState<number | null | 'information' | 'terminal'>(null);
  const [runInfo, setRunInfo] = useState<RunInfo>(createDefaultRunInfo());
  const [runIdsAndLabel, setRunIdsAndLabel] = useState<RunIdsAndLabel>(
    createDefaultRunIdsAndLabel(),
  );
  const [viewSettings, setViewSettings] = useState<ViewSettings>(defaultLogState.viewSettings);
  const [entries, setEntries] = useState<Entry[]>([]); // Start empty. Entries will be added as they're found.
  const lastUpdatedIndex = useRef<number>(0);

  // This works in the following way: whenever the item clicks an item to be expanded
  // the lastExpandedId is marked, then when filtering the children of the expanded
  // id are collected and this is later used to scroll the children into view.
  const lastExpandInfo = useRef<ExpandInfo>({
    lastExpandedId: '',
    idDepth: -1,
    childrenIndexes: new Set(),
  });

  /**
   * Register callback which should be used to set entries.
   */
  useEffect(() => {
    reactCallSetAllEntriesCallback(
      (allEntries: Entry[], newExpanded: string[], updatedFromIndex = 0) => {
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
          // console.log('Set entries to: ' + JSON.stringify(allEntries));
          lastUpdatedIndex.current = updatedFromIndex;
          return [...allEntries];
        });

        return undefined;
      },
    );

    reactCallSetRunInfoCallback((runInfo: RunInfo) => {
      setRunInfo(() => {
        return runInfo;
      });
    });

    reactCallSetRunIdsAndLabelCallback((runIdsAndLabel: RunIdsAndLabel) => {
      setRunIdsAndLabel(() => {
        return runIdsAndLabel;
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
        lastExpandInfo.current.lastExpandedId = '';
        lastExpandInfo.current.idDepth = -1;
        lastExpandInfo.current.childrenIndexes = new Set();
      } else {
        cp.add(id);
        lastExpandInfo.current.lastExpandedId = id;
        lastExpandInfo.current.idDepth = entryIdDepth(id);
        lastExpandInfo.current.childrenIndexes = new Set();
      }
      return cp;
    });
  }, []);

  // Leave only items which are actually expanded.
  const filteredEntries = useMemo(() => {
    if (filter !== undefined && filter.length > 0) {
      // Note: this also calls 'leaveOnlyExpandedEntries' internally.
      return leaveOnlyFilteredExpandedEntries(entries, expandedEntries, filter, lastExpandInfo);
    }
    return leaveOnlyExpandedEntries(entries, expandedEntries, lastExpandInfo);
  }, [entries, expandedEntries, filter, lastExpandInfo]);

  const ctx: LogContextType = {
    allEntries: entries,
    expandedEntries,
    filteredEntries,
    toggleEntry,
    activeIndex,
    setActiveIndex,
    viewSettings,
    setViewSettings,
    runInfo,
    lastUpdatedIndex,
    lastExpandInfo,
  };

  const logContextValue = useMemo(
    () => ctx,
    [entries, activeIndex, expandedEntries, filteredEntries, viewSettings, runInfo],
  );

  return (
    <ThemeProvider name={viewSettings.theme}>
      <Main>
        <LogContext.Provider value={logContextValue}>
          <HeaderAndMenu
            filter={filter}
            setFilter={setFilter}
            runInfo={runInfo}
            runIdsAndLabel={runIdsAndLabel}
          />
          <ListHeaderAndContents />
          <Details />
        </LogContext.Provider>
      </Main>
    </ThemeProvider>
  );
};

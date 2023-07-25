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
  IsExpanded,
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

  // Regular usage: user expands entries
  const [expandedEntries, setExpandedEntries] = useState<Set<string>>(new Set<string>());
  const [activeIndex, setActiveIndex] = useState<number | null | 'information' | 'terminal'>(null);
  const [runInfo, setRunInfo] = useState<RunInfo>(createDefaultRunInfo());
  const [runIdsAndLabel, setRunIdsAndLabel] = useState<RunIdsAndLabel>(
    createDefaultRunIdsAndLabel(),
  );
  const [viewSettings, setViewSettings] = useState<ViewSettings>(defaultLogState.viewSettings);
  const [entries, setEntries] = useState<Entry[]>([]); // Start empty. Entries will be added as they're found.
  const lastUpdatedIndex = useRef<number>(0);

  const idToEntry = useRef<Map<string, Entry>>(new Map());

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
      (allEntries: Entry[], newExpanded: string[], updatedFromIndex = -1) => {
        // Note: the updatedFromIndex is not used right now (it'd need to be)
        // translated to the compressed value, but we don't have the use case
        // for now, so, just ignore it.
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
          for (const entry of allEntries) {
            idToEntry.current.set(entry.id, entry);
          }
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

  const hasFilter = filter !== undefined && filter.length > 0;

  if (hasFilter) {
    // When a filter is applied just say that the whole tree changed.
    lastUpdatedIndex.current = 0;
  }

  let isExpanded: IsExpanded;

  // Toggle the expanded state.
  const toggleEntry = useCallback((id: string) => {
    setExpandedEntries((curr) => {
      const cp = new Set<string>(curr);
      const entry = idToEntry.current.get(id);
      if (entry !== undefined) {
        lastUpdatedIndex.current = entry.entryIndexCompressed;
      }

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

  isExpanded = useCallback(
    (id: string) => {
      return expandedEntries.has(id);
    },
    [expandedEntries],
  );

  // Leave only items which are actually expanded.
  const filteredEntries = useMemo(() => {
    if (hasFilter) {
      // Note: this also calls 'leaveOnlyExpandedEntries' internally.
      return leaveOnlyFilteredExpandedEntries(entries, isExpanded, filter, lastExpandInfo);
    }
    return leaveOnlyExpandedEntries(entries, isExpanded, lastExpandInfo);
  }, [entries, expandedEntries, filter, isExpanded, lastExpandInfo]);

  const ctx: LogContextType = {
    allEntries: entries,
    isExpanded,
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
    [entries, activeIndex, isExpanded, expandedEntries, filteredEntries, viewSettings, runInfo],
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

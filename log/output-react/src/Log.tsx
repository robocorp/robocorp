import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { ThemeProvider, styled } from '@robocorp/theme';
import {
  LogContext,
  defaultLogState,
  LogContextType,
  RunInfo,
  createDefaultRunInfo,
  RunIdsAndLabel,
  createDefaultRunIdsAndLabel,
  entryIdDepth,
  IsExpanded,
  DetailsIndexType,
  SearchInfoRequest,
  createDefaultSearchInfoRequest,
  leaveOnlyExpandedEntries,
  FocusIndexType,
  LastUpdatedIndex,
} from '~/lib';
import { Entry, ExpandInfo, ViewSettings } from './lib/types';
import {
  reactCallSetAllEntriesCallback,
  reactCallSetRunIdsAndLabelCallback,
  reactCallSetRunInfoCallback,
} from './treebuild/effectCallbacks';
import { leaveOnlyFilteredEntries } from './lib/filteringHelpers';
import { Details } from './components/details/Details';
import { HeaderAndMenu } from './components/header/HeaderAndMenu';
import { ListHeaderAndContents } from './components/list/ListHeaderAndContents';
import { getNextMtime, updateMtime, wasMtimeHandled } from './lib/mtime';

const Main = styled.main`
  display: grid;
  grid-auto-columns: 1fr;
  grid-template-rows: auto minmax(0, 1fr);
  height: 100vh;
`;

export const Log = () => {
  const [searchInfoRequest, setSearchInfoRequest] = useState<SearchInfoRequest>(
    createDefaultSearchInfoRequest(),
  );

  // Regular usage: user expands entries
  const [expandedEntries, setExpandedEntries] = useState<Set<string>>(new Set<string>());
  const [detailsIndex, setDetailsIndex] = useState<DetailsIndexType>(null);
  const [focusIndex, setFocusIndex] = useState<FocusIndexType>(null);
  const [runInfo, setRunInfo] = useState<RunInfo>(createDefaultRunInfo());
  const [runIdsAndLabel, setRunIdsAndLabel] = useState<RunIdsAndLabel>(
    createDefaultRunIdsAndLabel(),
  );
  const [viewSettings, setViewSettings] = useState<ViewSettings>(defaultLogState.viewSettings);
  const [entries, setEntries] = useState<Entry[]>([]); // Start empty. Entries will be added as they're found.
  const [lastUpdatedIndexFiltered, setLastUpdatedIndexFiltered] = useState<LastUpdatedIndex>({
    filteredIndex: -1,
    mtime: -1,
  });

  const idToEntry = useRef<Map<string, Entry>>(new Map());

  // This works in the following way: whenever the item clicks an item to be expanded
  // the lastExpandedId is marked, then when filtering the children of the expanded
  // id are collected and this is later used to scroll the children into view.
  const lastExpandInfo = useRef<ExpandInfo>({
    lastExpandedId: '',
    idDepth: -1,
    childrenIndexesFiltered: new Set(),
  });

  useEffect(() => {
    // When the filter is changed, just say that the whole tree changed
    // (i.e.: heights of the filtered items may have changed).
    setLastUpdatedIndexFiltered({ mtime: getNextMtime(), filteredIndex: 0 });
  }, [viewSettings.treeFilterInfo.showInTree]);

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

  let isExpanded: IsExpanded;

  // Toggle the expanded state.
  const toggleEntryExpandState = useCallback((id: string) => {
    setExpandedEntries((curr) => {
      const cp = new Set<string>(curr);
      const entry = idToEntry.current.get(id);
      if (entry !== undefined) {
        setLastUpdatedIndexFiltered((prev) => {
          const curr = prev.filteredIndex;
          if (curr < 0) {
            return { filteredIndex: entry.entryIndexFiltered, mtime: getNextMtime() };
          }
          if (!wasMtimeHandled('lastUpdatedIndex', prev.mtime)) {
            // The last one wasn't handled, we need to keep the lower value
            // -- the mtime can be kept though.
            return { filteredIndex: Math.min(entry.entryIndexFiltered, curr), mtime: prev.mtime };
          } else {
            return { filteredIndex: entry.entryIndexFiltered, mtime: getNextMtime() };
          }
        });
      }

      if (curr.has(id)) {
        cp.delete(id);
        lastExpandInfo.current.lastExpandedId = '';
        lastExpandInfo.current.idDepth = -1;
        lastExpandInfo.current.childrenIndexesFiltered = new Set();
      } else {
        cp.add(id);
        lastExpandInfo.current.lastExpandedId = id;
        lastExpandInfo.current.idDepth = entryIdDepth(id);
        lastExpandInfo.current.childrenIndexesFiltered = new Set();
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
    const filtered = leaveOnlyFilteredEntries(entries, viewSettings.treeFilterInfo);

    // After we've filtered the entries we must do the search to auto-expand and focus the
    // given entry (if we haven't handled the request yet).
    if (updateMtime('searchApplied', searchInfoRequest.requestMTime)) {
      console.log('Do search');
    }

    return leaveOnlyExpandedEntries(filtered, isExpanded, lastExpandInfo);
  }, [
    entries,
    expandedEntries,
    isExpanded,
    lastExpandInfo,
    viewSettings.treeFilterInfo,
    searchInfoRequest,
  ]);

  const ctx: LogContextType = {
    allEntries: entries,
    isExpanded,
    filteredEntries,
    toggleEntryExpandState,
    detailsIndex,
    setDetailsIndex,
    focusIndex,
    setFocusIndex,
    viewSettings,
    setViewSettings,
    runInfo,
    lastUpdatedIndexFiltered,
    setLastUpdatedIndexFiltered,
    lastExpandInfo,
  };

  const logContextValue = useMemo(
    () => ctx,
    [
      entries,
      detailsIndex,
      isExpanded,
      expandedEntries,
      filteredEntries,
      viewSettings,
      runInfo,
      lastUpdatedIndexFiltered,
    ],
  );

  return (
    <ThemeProvider name={viewSettings.theme}>
      <Main>
        <LogContext.Provider value={logContextValue}>
          <HeaderAndMenu
            searchInfoRequest={searchInfoRequest}
            setSearchInfoRequest={setSearchInfoRequest}
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

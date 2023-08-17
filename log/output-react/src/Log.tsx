import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { ThemeProvider, styled } from '@robocorp/theme';
import {
  LogContext,
  defaultLogState,
  LogContextType,
  RunInfo,
  RunIdsAndLabel,
  createDefaultRunIdsAndLabel,
  IsExpanded,
  DetailsIndexType,
  leaveOnlyExpandedEntries,
  FocusIndexType,
  InvalidateTree,
} from '~/lib';
import { EntriesAndIdToEntry, EntriesInfo, Entry, InfoForScroll, ViewSettings } from './lib/types';
import {
  reactCallSetAllEntriesCallback,
  reactCallSetRunIdsAndLabelCallback,
  reactCallSetRunInfoCallback,
} from './treebuild/effectCallbacks';
import { applyEntriesFilters } from './lib/filtering';
import { Details } from './components/details/Details';
import { HeaderAndMenu } from './components/header/HeaderAndMenu';
import { ListHeaderAndContents } from './components/list/ListHeaderAndContents';
import { getNextMtime } from './lib/mtime';
import { updateExpanded } from './lib/selections';

const Main = styled.main`
  display: grid;
  grid-auto-columns: 1fr;
  grid-template-rows: auto minmax(0, 1fr);
  height: 100vh;
`;

export const Log = () => {
  // The entries which should be shown expanded.
  const [expandedEntries, setExpandedEntries] = useState<Set<string>>(new Set<string>());

  const [detailsIndex, setDetailsIndex] = useState<DetailsIndexType>(null);
  const [focusIndex, setFocusIndex] = useState<FocusIndexType>(null);
  const [selectionIndex, setSelectionIndex] = useState<FocusIndexType>(null);
  const [runInfo, setRunInfo] = useState<RunInfo>(defaultLogState.runInfo);
  const [runIdsAndLabel, setRunIdsAndLabel] = useState<RunIdsAndLabel>(
    createDefaultRunIdsAndLabel(),
  );
  const [viewSettings, setViewSettings] = useState<ViewSettings>(defaultLogState.viewSettings);

  // Start empty. Entries will be added as they're found.
  // We receive all the entries and the idToEntry.
  const [entriesInput, setEntriesInput] = useState<EntriesAndIdToEntry>({
    allEntries: [],
    idToEntry: new Map(),
  });

  // We have to set the index from which point onward the list must be updated.
  const [invalidateTree, setInvalidateTree] = useState<InvalidateTree>({
    indexInTreeEntries: -1,
    mtime: -1,
  });

  // Use: setScrollToItem / setScrollToChildrenOf to update this information
  // so that a scroll is done to the needed entry.
  const scrollInfo = useRef<InfoForScroll>({
    scrollTargetId: '',
    idDepth: -1,
    mtime: -1,
    entriesInfo: undefined,
    mode: 'scrollToChildren',
  });

  useEffect(() => {
    // When the filter is changed, just say that the whole tree changed
    // (i.e.: heights of the filtered items may have changed).
    setInvalidateTree({ mtime: getNextMtime(), indexInTreeEntries: 0 });
  }, [viewSettings.treeFilterInfo.showInTree]);

  /**
   * Register callback which should be used to set entries.
   */
  useEffect(() => {
    reactCallSetAllEntriesCallback(
      (
        allEntries: Entry[],
        idToEntry: Map<string, Entry>,
        newExpanded: string[],
        updatedFromIndex = -1,
      ) => {
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

        setEntriesInput(() => {
          // console.log('Set entries to: ' + JSON.stringify(allEntries));

          // Note: we don't even copy it, just reuse the same instance
          // to be more efficient
          // (note that it can change accross runs).
          // We could create copies to be more "pure", but I couldn't find
          // a use case where getting a newer copy would be catastrophic.
          // Note that entries themselves are considered immutable.
          return { allEntries, idToEntry };
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

  // Remove items filtered out.
  const filtered: Entry[] = useMemo(() => {
    return applyEntriesFilters(entriesInput.allEntries, viewSettings.treeFilterInfo);
  }, [entriesInput, viewSettings.treeFilterInfo]);

  const isExpanded: IsExpanded = useCallback(
    (id: string) => {
      return expandedEntries.has(id);
    },
    [expandedEntries],
  );

  const entriesInfo: EntriesInfo = useMemo(() => {
    // Leave only items which are actually expanded.
    const treeEntries = leaveOnlyExpandedEntries(filtered, isExpanded);
    return {
      allEntries: entriesInput.allEntries,
      entriesWithFilterApplied: filtered,
      treeEntries,
      getEntryFromId: (id: string): Entry | undefined => {
        return entriesInput.idToEntry.get(id);
      },
    };
  }, [filtered, expandedEntries, entriesInput]);

  const updateExpandState = useCallback(
    (
      ids: string | string[],
      forceMode: 'expand' | 'collapse' | 'toggle' | 'expandSubTree' | 'collapseSubTree',
      scrollIntoView: boolean,
    ) => {
      if (typeof ids === 'string') {
        ids = [ids];
      }
      return updateExpanded(
        setExpandedEntries,
        setInvalidateTree,
        scrollInfo,
        entriesInfo,
        ids,
        forceMode,
        scrollIntoView,
      );
    },
    [entriesInfo],
  );

  const ctx: LogContextType = {
    entriesInfo,
    isExpanded,
    updateExpandState,
    detailsIndex,
    setDetailsIndex,
    focusIndex,
    setFocusIndex,
    selectionIndex,
    setSelectionIndex,
    viewSettings,
    setViewSettings,
    runInfo,
    invalidateTree,
    setInvalidateTree,
    scrollInfo,
  };

  scrollInfo.current.entriesInfo = entriesInfo;

  const logContextValue = useMemo(
    () => ctx,
    [
      entriesInfo,
      isExpanded,
      updateExpandState,
      detailsIndex,
      setDetailsIndex,
      focusIndex,
      setFocusIndex,
      selectionIndex,
      setSelectionIndex,
      viewSettings,
      setViewSettings,
      runInfo,
      invalidateTree,
      setInvalidateTree,
      scrollInfo,
    ],
  );

  return (
    // <StrictMode>
    <ThemeProvider name={viewSettings.theme}>
      <Main>
        <LogContext.Provider value={logContextValue}>
          <HeaderAndMenu runInfo={runInfo} runIdsAndLabel={runIdsAndLabel} />
          <ListHeaderAndContents />
          <Details />
        </LogContext.Provider>
      </Main>
    </ThemeProvider>
    // </StrictMode>
  );
};

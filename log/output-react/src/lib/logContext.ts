import { Dispatch, MutableRefObject, SetStateAction, createContext, useContext } from 'react';
import { Entry, ExpandInfo, StatusLevel, ViewSettings } from './types';
import { Counter, isDocumentDefined, isWindowDefined, logError } from './helpers';
import { detectVSCodeTheme } from '../vscode/themeDetector';
import { isInVSCode } from '../vscode/vscodeComm';

export interface FilteredEntries {
  entries: Entry[];
  entriesWithChildren: Set<string>;
}

export type RunInfoStatus = 'ERROR' | 'PASS' | 'UNSET';
export interface RunInfo {
  versionTooNew: boolean;
  version: string;
  description: string;
  time: string;
  status: RunInfoStatus;
  finishTimeDeltaInSeconds: number | undefined;
  firstPart: number;
  lastPart: number;
  infoMessages: Set<string>;
}

export interface SearchInfoRequest {
  searchValue: string;
  requestMTime: number;
  direction: 'forward' | 'backward';

  /**
   * In incremental mode it may keep on matching the same entry again
   * (used when changing the searchValue)
   */
  incremental: boolean;
  // isRegexp: boolean;
  // isWholeWord: boolean;
  // isCaseSensitive: boolean;
  lastFound: Entry | undefined;
}

export interface LastUpdatedIndex {
  filteredIndex: number;
  mtime: number;
}

export const createDefaultSearchInfoRequest = (): SearchInfoRequest => {
  return {
    searchValue: '',
    requestMTime: -1,
    direction: 'forward',
    incremental: true,
    lastFound: undefined,
  };
};

export interface RunIdsAndLabel {
  allRunIdsToLabel: Map<string, string>;
  currentRunId: string | undefined;
}

export interface IsExpanded {
  (id: string): boolean;
}

export interface DetailsIndexSelected {
  indexAll: number;
}

export interface FocusIndexSelected {
  indexAll: number;
  mtime: number;
}

export type DetailsIndexType = null | 'information' | 'terminal' | DetailsIndexSelected;
export type FocusIndexType = null | FocusIndexSelected;

export type LogContextType = {
  isExpanded: IsExpanded;
  allEntries: Entry[];
  filteredEntries: FilteredEntries;
  toggleEntryExpandState: (id: string) => void;
  detailsIndex: DetailsIndexType;
  setDetailsIndex: Dispatch<SetStateAction<DetailsIndexType>>;
  focusIndex: FocusIndexType;
  setFocusIndex: Dispatch<SetStateAction<FocusIndexType>>;
  viewSettings: ViewSettings;
  setViewSettings: Dispatch<SetStateAction<ViewSettings>>;
  runInfo: RunInfo;
  lastUpdatedIndexFiltered: LastUpdatedIndex;
  setLastUpdatedIndexFiltered: Dispatch<SetStateAction<LastUpdatedIndex>>;
  lastExpandInfo: MutableRefObject<ExpandInfo>;
};

let defaultTheme: 'light' | 'dark' = 'light';
try {
  // User can specify log.html?theme=dark|light in url.
  let s: string | null = '';
  if (isDocumentDefined()) {
    let params = new URLSearchParams(document?.location?.search);
    s = params.get('theme');
  }
  if (s === 'light' || s === 'dark') {
    defaultTheme = s;
  } else {
    // See if we can get it from VSCode:
    let vscodeTheme = detectVSCodeTheme();

    if (vscodeTheme === 'vscode-light') {
      defaultTheme = 'light';
    } else if (vscodeTheme === 'vscode-dark' || vscodeTheme === 'vscode-hc') {
      defaultTheme = 'dark';
    } else {
      // if not specified through url nor vscode, use from color scheme match.
      if (isWindowDefined() && window?.matchMedia) {
        if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
          defaultTheme = 'dark';
        } else if (window.matchMedia('(prefers-color-scheme: light)').matches) {
          defaultTheme = 'light';
        }
      }
    }
  }
} catch (err) {
  logError(err);
}

export const createDefaultRunInfo = (): RunInfo => ({
  version: '',
  versionTooNew: false,
  description: 'Wating for run to start ...',
  time: '',
  status: 'UNSET',
  finishTimeDeltaInSeconds: undefined,
  firstPart: -1,
  lastPart: -1,
  infoMessages: new Set<string>(),
});

export const createDefaultRunIdsAndLabel = (): RunIdsAndLabel => ({
  allRunIdsToLabel: new Map(),
  currentRunId: undefined,
});

export const defaultLogState: LogContextType = {
  allEntries: [],
  isExpanded: (id: string) => {
    return false;
  },
  filteredEntries: {
    entries: [],
    entriesWithChildren: new Set<string>(),
  },
  toggleEntryExpandState: () => null,
  detailsIndex: null,
  setDetailsIndex: () => null,
  focusIndex: null,
  setFocusIndex: () => null,
  viewSettings: {
    theme: defaultTheme,
    columns: {
      duration: true,
      location: true,
    },
    format: 'auto' as const,
    mode: isInVSCode() ? 'compact' : 'sparse',
    showInTerminal: StatusLevel.error,
    treeFilterInfo: {
      showInTree: StatusLevel.debug | StatusLevel.info | StatusLevel.warn | StatusLevel.error,
    },
  },
  setViewSettings: () => null,
  runInfo: createDefaultRunInfo(),
  setLastUpdatedIndexFiltered: () => null,
  lastUpdatedIndexFiltered: { filteredIndex: -1, mtime: -1 },
  lastExpandInfo: {
    current: {
      lastExpandedId: '',
      idDepth: -1,
      childrenIndexesFiltered: new Set(),
    },
  },
};

export const LogContext = createContext<LogContextType>(defaultLogState);

export const useLogContext = () => {
  return useContext(LogContext);
};

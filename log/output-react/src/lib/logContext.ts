import { Dispatch, MutableRefObject, SetStateAction, createContext, useContext } from 'react';
import {
  EntriesInfo,
  Entry,
  InfoForScroll,
  TreeEntries,
  StatusLevel,
  ViewSettings,
  createDefaultEntriesInfo,
} from './types';
import { isDocumentDefined, isWindowDefined, logError } from './helpers';
import { detectVSCodeTheme } from '../vscode/themeDetector';
import { isInVSCode } from '../vscode/vscodeComm';

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
  direction: 'forward' | 'backward';

  /**
   * In incremental mode it may keep on matching the same entry again
   * (used when changing the searchValue)
   */
  incremental: boolean;
  // isRegexp: boolean;
  // isWholeWord: boolean;
  // isCaseSensitive: boolean;
  requestMTime: number;
}

export interface SearchInfoResult {
  found: Entry | undefined;
  resultMTime: number;
}

export interface InvalidateTree {
  indexInTreeEntries: number;
  mtime: number;
}

export const createDefaultSearchInfoRequest = (): SearchInfoRequest => {
  return {
    searchValue: '',
    direction: 'forward',
    incremental: true,
    requestMTime: -1,
  };
};

export const createDefaultSearchInfoResult = (): SearchInfoResult => {
  return {
    found: undefined,
    resultMTime: -1,
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
export interface SelectionIndexSelected {
  indexAll: number;
  mtime: number;
}

export type DetailsIndexType = null | 'information' | 'terminal' | DetailsIndexSelected;
export type FocusIndexType = null | FocusIndexSelected;
export type SelectionIndexType = null | SelectionIndexSelected;

export type AnyIndexType = null | SelectionIndexType | FocusIndexType;

export type LogContextType = {
  isExpanded: IsExpanded;
  entriesInfo: EntriesInfo;
  updateExpandState: (
    id: string | string[],
    forceMode: 'expand' | 'toggle' | 'collapse' | 'expandSubTree' | 'collapseSubTree',
    scrollIntoView: boolean,
  ) => boolean;
  detailsIndex: DetailsIndexType;
  setDetailsIndex: Dispatch<SetStateAction<DetailsIndexType>>;
  focusIndex: FocusIndexType;
  setFocusIndex: Dispatch<SetStateAction<FocusIndexType>>;
  selectionIndex: SelectionIndexType;
  setSelectionIndex: Dispatch<SetStateAction<SelectionIndexType>>;
  viewSettings: ViewSettings;
  setViewSettings: Dispatch<SetStateAction<ViewSettings>>;
  runInfo: RunInfo;
  invalidateTree: InvalidateTree;
  setInvalidateTree: Dispatch<SetStateAction<InvalidateTree>>;
  scrollInfo: MutableRefObject<InfoForScroll>;
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
  description: 'Waiting for run to start ...',
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
  entriesInfo: createDefaultEntriesInfo(),
  isExpanded: (id: string) => {
    return false;
  },
  updateExpandState: () => true,
  detailsIndex: null,
  setDetailsIndex: () => null,
  focusIndex: null,
  setFocusIndex: () => null,
  selectionIndex: null,
  setSelectionIndex: () => null,
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
  setInvalidateTree: () => null,
  invalidateTree: { indexInTreeEntries: -1, mtime: -1 },
  scrollInfo: {
    current: {
      mode: 'scrollToItem',
      scrollTargetId: '',
      idDepth: -1,
      entriesInfo: undefined,
      mtime: -1,
    },
  },
};

export const LogContext = createContext<LogContextType>(defaultLogState);

export const useLogContext = () => {
  return useContext(LogContext);
};

import { Dispatch, MutableRefObject, SetStateAction, createContext, useContext } from 'react';
import { Entry, ExpandInfo, StatusLevel, ViewSettings } from './types';
import { isDocumentDefined, isWindowDefined, logError } from './helpers';
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

export interface RunIdsAndLabel {
  allRunIdsToLabel: Map<string, string>;
  currentRunId: string | undefined;
}

export type LogContextType = {
  expandedEntries: Set<string>;
  allEntries: Entry[];
  filteredEntries: FilteredEntries;
  toggleEntry: (id: string) => void;
  activeIndex: null | number | 'information' | 'terminal';
  setActiveIndex: (index: null | number | 'information' | 'terminal') => void;
  viewSettings: ViewSettings;
  setViewSettings: Dispatch<SetStateAction<ViewSettings>>;
  runInfo: RunInfo;
  lastUpdatedIndex: MutableRefObject<number>;
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
  expandedEntries: new Set<string>(),
  filteredEntries: {
    entries: [],
    entriesWithChildren: new Set<string>(),
  },
  toggleEntry: () => null,
  activeIndex: null,
  setActiveIndex: () => null,
  viewSettings: {
    theme: defaultTheme,
    columns: {
      duration: true,
      location: true,
    },
    format: 'auto' as const,
    mode: isInVSCode() ? 'compact' : 'sparse',
    showInTerminal: StatusLevel.error,
  },
  setViewSettings: () => null,
  runInfo: createDefaultRunInfo(),
  lastUpdatedIndex: { current: 0 },
  lastExpandInfo: {
    current: {
      lastExpandedId: '',
      idDepth: -1,
      childrenIndexes: new Set(),
    },
  },
};

export const LogContext = createContext<LogContextType>(defaultLogState);

export const useLogContext = () => {
  return useContext(LogContext);
};

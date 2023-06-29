import { Dispatch, MutableRefObject, SetStateAction, createContext, useContext } from 'react';
import { Entry, ViewSettings } from './types';
import { logError } from './helpers';

export interface FilteredEntries {
  entries: Entry[];
  entriesWithChildren: Set<string>;
}

export type RunInfoStatus = 'ERROR' | 'PASS' | 'UNSET';
export interface RunInfo {
  description: string;
  time: string;
  status: RunInfoStatus;
  finishTimeDeltaInSeconds: number | undefined;
  firstPart: number;
  lastPart: number;
  infoMessages: Set<string>;
}

export type LogContextType = {
  expandedEntries: Set<string>;
  filteredEntries: FilteredEntries;
  toggleEntry: (id: string) => void;
  activeIndex: null | number | 'information';
  setActiveIndex: (index: null | number | 'information') => void;
  viewSettings: ViewSettings;
  setViewSettings: Dispatch<SetStateAction<ViewSettings>>;
  runInfo: RunInfo;
  lastUpdatedIndex: MutableRefObject<number>;
};

let defaultTheme: 'light' | 'dark' = 'light';
try {
  // User can specify log.html?theme=dark|light in url.
  const params = new URLSearchParams(document.location.search);
  const s = params.get('theme');
  if (s === 'light' || s === 'dark') {
    defaultTheme = s;
  } else {
    // if not specified through url, use from color scheme match.
    if (window.matchMedia) {
      if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
        defaultTheme = 'dark';
      } else if (window.matchMedia('(prefers-color-scheme: light)').matches) {
        defaultTheme = 'light';
      }
    }
  }
} catch (err) {
  logError(err);
}

export const createDefaultRunInfo = (): RunInfo => ({
  description: 'Wating for run to start ...',
  time: '',
  status: 'UNSET',
  finishTimeDeltaInSeconds: undefined,
  firstPart: -1,
  lastPart: -1,
  infoMessages: new Set<string>(),
});

export const defaultLogState: LogContextType = {
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
  },
  setViewSettings: () => null,
  runInfo: createDefaultRunInfo(),
  lastUpdatedIndex: { current: 0 },
};

export const LogContext = createContext<LogContextType>(defaultLogState);

export const useLogContext = () => {
  return useContext(LogContext);
};

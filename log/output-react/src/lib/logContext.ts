import { Dispatch, MutableRefObject, SetStateAction, createContext, useContext } from 'react';
import { Entry, ViewSettings } from './types';

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
}

export type LogContextType = {
  expandedEntries: Set<string>;
  filteredEntries: FilteredEntries;
  toggleEntry: (id: string) => void;
  activeIndex: null | number;
  setActiveIndex: (index: null | number) => void;
  viewSettings: ViewSettings;
  setViewSettings: Dispatch<SetStateAction<ViewSettings>>;
  runInfo: RunInfo;
  lastUpdatedIndex: MutableRefObject<number>;
};

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
    theme: 'light' as const,
    columns: {
      duration: true,
      location: true,
    },
  },
  setViewSettings: () => null,
  runInfo: {
    description: 'Wating for run to start ...',
    time: '',
    status: 'UNSET',
    finishTimeDeltaInSeconds: undefined,
  },
  lastUpdatedIndex: { current: 0 },
};

export const LogContext = createContext<LogContextType>(defaultLogState);

export const useLogContext = () => {
  return useContext(LogContext);
};

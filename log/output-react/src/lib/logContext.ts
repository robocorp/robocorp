import { Dispatch, MutableRefObject, SetStateAction, createContext, useContext } from 'react';
import { Entry, ViewSettings } from './types';

export interface FilteredEntries {
  entries: Entry[];
  entriesWithChildren: Set<string>;
}

export type LogContextType = {
  expandedEntries: Set<string>;
  filteredEntries: FilteredEntries;
  toggleEntry: (id: string) => void;
  activeIndex: null | number;
  setActiveIndex: (index: null | number) => void;
  viewSettings: ViewSettings;
  setViewSettings: Dispatch<SetStateAction<ViewSettings>>;
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
  lastUpdatedIndex: { current: 0 },
};

export const LogContext = createContext<LogContextType>(defaultLogState);

export const useLogContext = () => {
  return useContext(LogContext);
};

import { Dispatch, MutableRefObject, SetStateAction, createContext, useContext } from 'react';
import { Entry, ViewSettings } from './types';

export const defaultLogState = {
  entries: [],
  expandedEntries: [],
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

type LogContext = {
  entries: Entry[];
  expandedEntries: string[];
  toggleEntry: (id: string) => void;
  activeIndex: null | number;
  setActiveIndex: (index: null | number) => void;
  viewSettings: ViewSettings;
  setViewSettings: Dispatch<SetStateAction<ViewSettings>>;
  lastUpdatedIndex: MutableRefObject<number>;
};

export const LogContext = createContext<LogContext>(defaultLogState);

export const useLogContext = () => {
  return useContext(LogContext);
};

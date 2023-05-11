import { Dispatch, SetStateAction, createContext, useContext } from 'react';
import { Entry, ViewSettings } from './types';

export const defaultLogState = {
  entries: [],
  expandedEntries: [],
  toggleEntry: () => null,
  activeIndex: null,
  setActiveIndex: () => null,
  viewSettings: {
    theme: 'light',
    columns: {
      duration: true,
      location: true,
    },
  },
  setViewSettings: () => null,
};

type LogContext = {
  entries: Entry[];
  expandedEntries: string[];
  toggleEntry: (id: string) => void;
  activeIndex: null | number;
  setActiveIndex: (index: null | number) => void;
  viewSettings: ViewSettings;
  setViewSettings: Dispatch<SetStateAction<ViewSettings>>;
};

export const LogContext = createContext<LogContext>(defaultLogState);

export const useLogContext = () => {
  return useContext(LogContext);
};

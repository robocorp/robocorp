import { Dispatch, SetStateAction, createContext, useContext } from 'react';
import { LoadedActionsPackages, LoadedRuns, ServerConfig } from './types';

export type ViewSettings = {
  theme: 'dark' | 'light';
};

export type ActionServerContextType = {
  viewSettings: ViewSettings;
  setViewSettings: Dispatch<SetStateAction<ViewSettings>>;
  loadedRuns: LoadedRuns;
  setLoadedRuns: Dispatch<SetStateAction<LoadedRuns>>;
  loadedActions: LoadedActionsPackages;
  setLoadedActions: Dispatch<SetStateAction<LoadedActionsPackages>>;
  serverConfig?: ServerConfig;
};

export const defaultActionServerState: ActionServerContextType = {
  viewSettings: {
    theme: 'dark',
  },
  setViewSettings: () => null,

  // Runs
  loadedRuns: {
    isPending: true,
    data: [],
    errorMessage: undefined,
  },
  setLoadedRuns: () => null,

  // Actions
  loadedActions: {
    isPending: true,
    data: [],
    errorMessage: undefined,
  },
  setLoadedActions: () => null,
};

export const ActionServerContext = createContext<ActionServerContextType>(defaultActionServerState);

export const useActionServerContext = () => {
  return useContext(ActionServerContext);
};

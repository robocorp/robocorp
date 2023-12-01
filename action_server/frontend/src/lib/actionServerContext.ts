import { Dispatch, SetStateAction, createContext, useContext } from 'react';
import { isDocumentDefined, isWindowDefined, logError } from './helpers';
import { LoadedActions, LoadedRuns, Run } from './types';

export let defaultTheme: 'light' | 'dark' = 'light';
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
    // if not specified through url, use from color scheme match.
    if (isWindowDefined() && window?.matchMedia) {
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

export type ViewSettings = {
  theme: 'dark' | 'light';
};

export type ActionServerContextType = {
  viewSettings: ViewSettings;
  setViewSettings: Dispatch<SetStateAction<ViewSettings>>;
  loadedRuns: LoadedRuns;
  setLoadedRuns: Dispatch<SetStateAction<LoadedRuns>>;
  loadedActions: LoadedActions;
  setLoadedActions: Dispatch<SetStateAction<LoadedActions>>;
};

export const defaultActionServerState: ActionServerContextType = {
  viewSettings: {
    theme: defaultTheme,
  },
  setViewSettings: () => null,

  // Runs
  loadedRuns: {
    isPending: true,
    requestedOnce: false,
    data: [],
    errorMessage: undefined,
  },
  setLoadedRuns: () => null,

  // Actions
  loadedActions: {
    isPending: true,
    requestedOnce: false,
    data: [],
    errorMessage: undefined,
  },
  setLoadedActions: () => null,
};

export const ActionServerContext = createContext<ActionServerContextType>(defaultActionServerState);

export const useActionServerContext = () => {
  return useContext(ActionServerContext);
};

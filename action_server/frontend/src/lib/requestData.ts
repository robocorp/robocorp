import { Dispatch, SetStateAction } from 'react';
import { debounce } from './debounce';
import { LoadedActions, LoadedRuns, Run } from './types';
import { logError } from './helpers';

const baseUrl = '';
// const baseUrl = 'http://localhost:8090'

const createFunc = (url: string, method = 'GET'): any => {
  const ret = async (loaded: any, setterFromReact: Dispatch<SetStateAction<any>>) => {
    try {
      if (loaded.requestedOnce) {
        return;
      }
      setterFromReact(() => {
        return {
          isPending: true,
          data: loaded.data,
          requestedOnce: true,
        };
      });

      //   await new Promise(r => setTimeout(r, 3000));

      const res = await fetch(url, {
        method: method,
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json',
        },
        // body: '', // JSON.stringify({a: 1, b: 2})
      });
      if (!res.ok) {
        setterFromReact(() => {
          return {
            isPending: false,
            data: [],
            errorMessage: res.statusText,
            requestedOnce: true,
          };
        });
      } else {
        const loaded = (await res.json()) as unknown as Run[];
        setterFromReact(() => {
          return {
            isPending: false,
            data: loaded,
            requestedOnce: true,
          };
        });
      }
    } catch (err) {
      logError(err);
      return {
        isPending: false,
        data: [],
        errorMessage: JSON.stringify(err),
        requestedOnce: true,
      };
    }
  };
  return ret;
};

const debouncedLoadRuns = debounce(createFunc(baseUrl + '/api/runs/', 'GET'), 300);

export const refreshRuns = async (
  loadedRuns: LoadedRuns,
  setLoadedRuns: Dispatch<SetStateAction<LoadedRuns>>,
) => {
  debouncedLoadRuns(loadedRuns, setLoadedRuns);
};

const debouncedLoadActions = debounce(createFunc(baseUrl + '/api/actionPackages/', 'GET'), 300);

export const refreshActions = async (
  loadedActions: LoadedActions,
  setLoadedActions: Dispatch<SetStateAction<LoadedActions>>,
) => {
  debouncedLoadActions(loadedActions, setLoadedActions);
};

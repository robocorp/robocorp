import { Dispatch, SetStateAction } from 'react';
import { debounce } from './debounce';
import { AsyncLoaded, LoadedActionsPackages, LoadedRuns, Run } from './types';
import { logError } from './helpers';

const baseUrl = '';
// const baseUrl = 'http://localhost:8090';

interface Opts {
  body: string;
  params: Record<string, string>;
}

const createFunc = (url: string, method = 'GET'): any => {
  const ret = async (
    loaded: AsyncLoaded<any>,
    setterFromReact: Dispatch<SetStateAction<AsyncLoaded<any>>>,
    opts: Opts | undefined,
  ) => {
    const body: string | undefined = opts?.body;
    const params: Record<string, string> | undefined = opts?.params;
    if (params) {
      url += `?${new URLSearchParams(params)}`;
    }

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

      const fetchArgs: RequestInit = {
        method: method,
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json',
        },
      };
      if (body !== undefined) {
        fetchArgs['body'] = body;
      }
      const res = await fetch(url, fetchArgs);

      if (!res.ok) {
        setterFromReact(() => {
          return {
            isPending: false,
            data: [],
            errorMessage: `${res.status} (${res.statusText})`,
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
      setterFromReact(() => {
        return {
          isPending: false,
          data: [],
          errorMessage: JSON.stringify(err),
          requestedOnce: true,
        };
      });
    }
  };
  return ret;
};

const debouncedLoadRuns = debounce(createFunc(baseUrl + '/api/runs', 'GET'), 300);

export const refreshRuns = async (
  loadedRuns: LoadedRuns,
  setLoadedRuns: Dispatch<SetStateAction<LoadedRuns>>,
) => {
  debouncedLoadRuns(loadedRuns, setLoadedRuns);
};

const debouncedLoadActions = debounce(createFunc(baseUrl + '/api/actionPackages', 'GET'), 300);

export const refreshActions = async (
  loadedActions: LoadedActionsPackages,
  setLoadedActions: Dispatch<SetStateAction<LoadedActionsPackages>>,
) => {
  debouncedLoadActions(loadedActions, setLoadedActions);
};

export const collectRunArtifacts = (
  runId: string,
  artifactNames: string[],
  loaded: AsyncLoaded<any>,
  setLoaded: Dispatch<SetStateAction<AsyncLoaded<any>>>,
) => {
  const func = createFunc(baseUrl + `/api/runs/${runId}/artifacts/text-content`, 'GET');
  return func(loaded, setLoaded, { params: { artifact_names: artifactNames} });
};

/**
 * Runs the backend action and calls the `setLoaded` depending on the current state.
 */
export const runAction = (
  actionPackageName: string,
  actionName: string,
  args: object,
  loaded: AsyncLoaded<any>,
  setLoaded: Dispatch<SetStateAction<AsyncLoaded<any>>>,
) => {
  const func = createFunc(baseUrl + `/api/actions/${actionPackageName}/${actionName}/run`, 'POST');
  return func(loaded, setLoaded, { body: JSON.stringify(args) });
};

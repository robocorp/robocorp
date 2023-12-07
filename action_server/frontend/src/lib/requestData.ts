import { Dispatch, SetStateAction } from 'react';
import { AsyncLoaded, LoadedActionsPackages, LoadedRuns } from './types';
import { logError } from './helpers';
import { CachedModel, ModelContainer, ModelType } from './modelContainer';

export const baseUrl = '';
// export const baseUrl = 'http://localhost:8090';

interface Opts {
  body?: string;
  params?: Record<string, string>;
}

const _loadAsync = async (
  url: string,
  method: 'POST' | 'GET',
  opts: Opts | undefined = undefined,
): Promise<CachedModel> => {
  try {
    const body: string | undefined = opts?.body;
    const params: Record<string, string> | undefined = opts?.params;
    if (params) {
      url += `?${new URLSearchParams(params)}`;
    }

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
      return {
        isPending: false,
        data: undefined,
        errorMessage: `${res.status} (${res.statusText})`,
      };
    } else {
      const loadedResultAsJson = await res.json();
      return {
        isPending: false,
        data: loadedResultAsJson,
      };
    }
  } catch (err) {
    logError(err);
    return {
      isPending: false,
      data: undefined,
      errorMessage: JSON.stringify(err),
    };
  }
};

const modelContainer = new ModelContainer();

class ModelUpdater {
  private modelContainer: ModelContainer;

  constructor(modelContainer: ModelContainer) {
    this.modelContainer = modelContainer;
  }

  public async startUpdating() {
    const loadActionsPromise = _loadAsync(baseUrl + '/api/actionPackages', 'GET');
    const loadRunsPromise = _loadAsync(baseUrl + '/api/runs', 'GET');

    const actions = await loadActionsPromise;
    const runs = await loadRunsPromise;

    modelContainer.onModelUpdated(ModelType.ACTIONS, actions);
    modelContainer.onModelUpdated(ModelType.RUNS, runs);
  }
}

const modelUpdater = new ModelUpdater(modelContainer);
modelUpdater.startUpdating();

export const startTrackRuns = (setLoadedRuns: Dispatch<SetStateAction<LoadedRuns>>) => {
  modelContainer.addListener(ModelType.RUNS, setLoadedRuns);
};

export const startTrackActions = (
  setLoadedActions: Dispatch<SetStateAction<LoadedActionsPackages>>,
) => {
  modelContainer.addListener(ModelType.ACTIONS, setLoadedActions);
};

export const stopTrackRuns = (setLoadedRuns: Dispatch<SetStateAction<LoadedRuns>>) => {
  modelContainer.removeListener(ModelType.ACTIONS, setLoadedRuns);
};

export const stopTrackActions = (
  setLoadedActions: Dispatch<SetStateAction<LoadedActionsPackages>>,
) => {
  modelContainer.removeListener(ModelType.ACTIONS, setLoadedActions);
};

export const collectRunArtifacts = async (
  runId: string,
  setLoaded: Dispatch<SetStateAction<AsyncLoaded<any>>>,
  params: any,
) => {
  setLoaded({
    isPending: true,
    data: undefined,
  });
  const data = await _loadAsync(baseUrl + `/api/runs/${runId}/artifacts/text-content`, 'GET', {
    params: params,
  });
  setLoaded(data);
};

/**
 * Runs the backend action and calls the `setLoaded` depending on the current state.
 * No caching for this API.
 */
export const runAction = async (
  actionPackageName: string,
  actionName: string,
  args: object,
  setLoaded: Dispatch<SetStateAction<AsyncLoaded<any>>>,
) => {
  setLoaded({
    isPending: true,
    data: undefined,
  });
  const data = await _loadAsync(
    baseUrl + `/api/actions/${actionPackageName}/${actionName}/run`,
    'POST',
    { body: JSON.stringify(args) },
  );
  setLoaded(data);
};

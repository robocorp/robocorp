/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable max-classes-per-file */

import { Dispatch, SetStateAction } from 'react';
import {
  Action,
  ActionPackage,
  AsyncLoaded,
  LoadedActionsPackages,
  LoadedRuns,
  Run,
} from './types';
import { Counter, copyArrayAndInsertElement, logError } from './helpers';
import { CachedModel, ModelContainer, ModelType } from './modelContainer';
import { WebsocketConn } from './websocketConn';

export const baseUrl = '';
export const baseUrlWs = `ws://${window.location.host}`;
// export const baseUrl = 'http://localhost:8080';
// export const baseUrlWs = 'ws://localhost:8080';

interface Opts {
  body?: string;
  params?: Record<string, string>;
}

const loadAsync = async <T>(
  url: string,
  method: 'POST' | 'GET',
  opts: Opts | undefined = undefined,
  headers: HeadersInit | undefined = undefined,
): Promise<CachedModel<T>> => {
  try {
    const body: string | undefined = opts?.body;
    const params: Record<string, string> | undefined = opts?.params;
    let requestURL = url;

    if (params) {
      requestURL += `?${new URLSearchParams(params)}`;
    }

    const fetchArgs: RequestInit = {
      method,
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        ...headers,
      },
    };
    if (body !== undefined) {
      fetchArgs.body = body;
    }
    const res = await fetch(requestURL, fetchArgs);

    if (!res.ok) {
      return {
        isPending: false,
        data: undefined,
        errorMessage: `${res.status} (${res.statusText})`,
      };
    }
    const loadedResultAsJson = await res.json();
    return {
      isPending: false,
      data: loadedResultAsJson,
    };
  } catch (err) {
    logError(err);
    return {
      isPending: false,
      data: undefined,
      errorMessage: err instanceof Error ? err.message : JSON.stringify(err),
    };
  }
};

const globalModelContainer = new ModelContainer();

/**
 * Runs are sorted in descending order as this is the way we
 * should usually iterate over it.
 */
const sortRuns = (runs: Run[]): void => {
  runs.sort((a: Run, b: Run) => b.numbered_id - a.numbered_id);
};

const globalCounter = new Counter();

interface IRequest {
  method: 'POST' | 'GET';
  url: string;
}

interface IResponse<T> {
  result: T;
}

class ModelUpdater {
  private modelContainer: ModelContainer;

  private sio: WebsocketConn;

  private messageIdToHandler = new Map();

  constructor(modelContainer: ModelContainer) {
    this.modelContainer = modelContainer;
    this.sio = new WebsocketConn(`${baseUrlWs}/api/ws`);

    this.sio.on('echo', (echoVal: string) => {
      // console.log('echo val was', echoVal);
    });

    this.sio.on('runs_collected', (runs: any) => {
      // console.log('runs collected', runs);
      sortRuns(runs);

      this.modelContainer.onModelUpdated(ModelType.RUNS, { isPending: false, data: runs });
    });

    this.sio.on('run_added', (data: any) => {
      // console.log('run added', data);
      const { run } = data;
      const runsModel = this.modelContainer.getCurrentModel<Run>(ModelType.RUNS);
      // Runs should be reverse ordered by their id.
      if (runsModel !== undefined && runsModel.data !== undefined && !runsModel.isPending) {
        // Insert but make sure we keep the (reverse) order.
        let newRunData;
        for (let i = 0; i < runsModel.data.length - 1; i += 1) {
          if (run.numbered_id > runsModel.data[i].numbered_id) {
            newRunData = copyArrayAndInsertElement(runsModel.data, run, i);
            break;
          }
        }
        if (newRunData === undefined) {
          // Case for len==0 or if it was lowest than any existing run.
          newRunData = runsModel.data.slice();
          newRunData.push(run);
        }
        this.modelContainer.onModelUpdated(ModelType.RUNS, {
          isPending: false,
          data: newRunData,
        });
      }
    });

    this.sio.on('run_changed', (run: any) => {
      // console.log('run changed', run);
      const runId = run.run_id;
      const { changes } = run;

      const runsModel = this.modelContainer.getCurrentModel<Run>(ModelType.RUNS);
      if (runsModel !== undefined && runsModel.data !== undefined) {
        // Runs should be reverse ordered by their id and changes are
        // usually in the latest runs, so, just iterating to find
        // that should actually be fast as it should be one
        // of the first items.
        for (let i = 0; i < runsModel.data.length; i += 1) {
          if (runId === runsModel.data[i].id) {
            const run = runsModel.data[i];
            const newRun = { ...run, ...changes };
            const newRunData = runsModel.data.slice();
            newRunData[i] = newRun;
            this.modelContainer.onModelUpdated(ModelType.RUNS, {
              isPending: false,
              data: newRunData,
            });
            break;
          }
        }
      }
    });

    this.sio.on('response', (response: any) => {
      // console.log('response', response);
      const messageId = response.message_id;
      const handler = this.messageIdToHandler.get(messageId);
      if (handler !== undefined) {
        this.messageIdToHandler.delete(messageId);
        handler(response);
      } else {
        // eslint-disable-next-line no-console
        console.log(`Error: no handler for response: ${JSON.stringify(response)}`);
      }
    });

    this.sio.on('connect', () => {
      // On any new connection we have to start listening again
      // (either being the first or not as new connections later
      // on probably mean we missed updates).
      this.sio.emit('start_listen_run_events');
    });
  }

  public async startUpdating() {
    // Load initial data (actions/runs)
    const loadActionsPromise = loadAsync<Action>(`${baseUrl}/api/actionPackages`, 'GET');
    const loadRunsPromise = loadAsync<Run>(`${baseUrl}/api/runs`, 'GET');

    const actions = await loadActionsPromise;
    const runs = await loadRunsPromise;

    if (runs.data !== undefined) {
      sortRuns(runs.data);
    }

    this.modelContainer.onModelUpdated(ModelType.ACTIONS, actions);
    this.modelContainer.onModelUpdated(ModelType.RUNS, runs);

    // Connect now to automatically start tracking run changes.
    this.sio.connect();
  }

  public async request<T>(req: IRequest): Promise<IResponse<T>> {
    let onResolve: (value: IResponse<T>) => void;

    const promise: Promise<IResponse<T>> = new Promise((resolve) => {
      onResolve = resolve;
    });

    const messageHandler = (response: IResponse<T>) => {
      // TODO: See what'd be a response error.
      onResolve(response);
    };

    const messageId = globalCounter.next();
    this.messageIdToHandler.set(messageId, messageHandler);
    this.sio.emit('request', { method: req.method, url: req.url, message_id: messageId });

    return promise;
  }
}

const globalModelUpdater = new ModelUpdater(globalModelContainer);
globalModelUpdater.startUpdating();

export const startTrackRuns = (setLoadedRuns: Dispatch<SetStateAction<LoadedRuns>>) => {
  globalModelContainer.addListener(ModelType.RUNS, setLoadedRuns);
};

export const startTrackActions = (
  setLoadedActions: Dispatch<SetStateAction<LoadedActionsPackages>>,
) => {
  globalModelContainer.addListener(ModelType.ACTIONS, setLoadedActions);
};

export const stopTrackRuns = (setLoadedRuns: Dispatch<SetStateAction<LoadedRuns>>) => {
  globalModelContainer.removeListener(ModelType.ACTIONS, setLoadedRuns);
};

export const stopTrackActions = (
  setLoadedActions: Dispatch<SetStateAction<LoadedActionsPackages>>,
) => {
  globalModelContainer.removeListener(ModelType.ACTIONS, setLoadedActions);
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
  const data = await loadAsync(`${baseUrl}/api/runs/${runId}/artifacts/text-content`, 'GET', {
    params,
  });
  setLoaded(data);
};

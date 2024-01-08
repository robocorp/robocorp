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

export const baseUrl = '';
export const baseUrlWs = `ws://${window.location.host}`;

interface Opts {
  body?: string;
  params?: Record<string, string>;
}

const loadAsync = async <T>(
  url: string,
  method: 'POST' | 'GET',
  opts: Opts | undefined = undefined,
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

export class WebsocketConn {
  private ws: WebSocket | null = null;

  private connected = false;

  private connecting = false;

  // TODO: Make ping-pong to verify if it's still alive.
  private lastPingTime = 0;

  private lastPongTime = 0;
  // this.lastPingTime = performance.now();

  constructor(
    private url: string,
    private onReceivedMessage: (event: MessageEvent) => void,
  ) {
    this.url = url;
    this.onReceivedMessage = onReceivedMessage;
  }

  public connect(): Promise<void> {
    this.connecting = true;
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        this.connected = true;
        this.connecting = false;
        resolve();
      };

      this.ws.onmessage = this.handleMessage;
      this.ws.onclose = this.handleClose;
      const markNotConnectingAndReject = () => {
        this.connected = false;
        this.connecting = false;
        reject();
      };
      this.ws.onerror = markNotConnectingAndReject;
    });
  }

  public isConnected() {
    if (this.ws && this.connected) {
      return true;
    }
    return false;
  }

  public isConnecting() {
    if (this.ws && this.connecting) {
      return true;
    }
    return false;
  }

  public send(message: string | ArrayBuffer): void {
    if (!this.isConnected() || !this.ws) {
      throw new Error('Unable to send, websocket is not connected');
    }
    // That's sync but it doesn't block (just enqueues data to send).
    this.ws.send(message);
  }

  public close(): void {
    if (this.ws) {
      this.connected = false;
      this.connecting = false;
      const { ws } = this;
      this.ws = null;
      ws.close();
    }
  }

  private handleMessage = (message: MessageEvent) => {
    this.onReceivedMessage(message);
  };

  private handleClose = () => {
    this.connected = false;
    this.connecting = false;

    if (!this.ws) {
      // It was finished for good.
      return;
    }

    setTimeout(() => {
      this.connect();
    }, 5000);
  };
}

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

  private conn: WebsocketConn;

  private messageIdToHandler = new Map();

  constructor(modelContainer: ModelContainer) {
    this.modelContainer = modelContainer;
    this.conn = new WebsocketConn(`${baseUrlWs}/api/ws`, this.onReceivedMessage.bind(this));
  }

  public async onReceivedMessage(message: MessageEvent) {
    const dataStr = message.data;
    if (dataStr) {
      const data = JSON.parse(dataStr);
      const messageType = data.message_type;

      if (messageType === 'runs_collected') {
        const { runs } = data;
        sortRuns(runs);

        this.modelContainer.onModelUpdated(ModelType.RUNS, { isPending: false, data: runs });
      } else if (messageType === 'run_added') {
        const runsModel = this.modelContainer.getCurrentModel<Run>(ModelType.RUNS);
        // Runs should be reverse ordered by their id.
        if (runsModel !== undefined && runsModel.data !== undefined && !runsModel.isPending) {
          const { run } = data;
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
      } else if (messageType === 'response') {
        const responseData = data.data;
        const messageId = responseData.message_id;
        const handler = this.messageIdToHandler.get(messageId);
        if (handler !== undefined) {
          this.messageIdToHandler.delete(messageId);
          handler(responseData);
        } else {
          // eslint-disable-next-line no-console
          console.log(`Error: no handler for response: ${JSON.stringify(data)}`);
        }
      } else if (messageType === 'run_changed') {
        const runId = data.run_id;
        const { changes } = data;

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
      }
    }
  }

  private async request<T>(req: IRequest): Promise<IResponse<T>> {
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

    const msg = JSON.stringify({
      message_type: 'request',
      data: { method: req.method, url: req.url, message_id: messageId },
    });

    this.conn.send(msg);

    return promise;
  }

  public async startUpdating() {
    if (!this.conn.isConnected() && !this.conn.isConnecting()) {
      const connectPromise = this.conn.connect();
      const timeoutPromise = new Promise((resolve, reject) => {
        setTimeout(() => reject(new Error('Timeout')), 5000);
      });

      try {
        await Promise.race([connectPromise, timeoutPromise]);
      } catch (error) {
        // timed out, let's stop waiting and go without websockets
      }
    }

    if (this.conn.isConnected()) {
      // Use websocket when we can.
      this.conn.send(JSON.stringify({ message_type: 'start_listen_run_events' }));

      // Everything available through a regular connection is also available through
      // the websocket (that is better when available).
      this.modelContainer.onModelUpdated(
        ModelType.ACTIONS,
        await loadAsync<Action>(`${baseUrl}/api/actionPackages`, 'GET'),
      );

      const loadActionsPromise = this.request<ActionPackage[]>({
        method: 'GET',
        url: '/api/actionPackages',
      });

      loadActionsPromise.then((actions) => {
        this.modelContainer.onModelUpdated(ModelType.ACTIONS, {
          isPending: false,
          data: actions.result,
        });
      });
    } else {
      // eslint-disable-next-line no-console
      console.log(
        'Unable to use websockets (no connection was made in 5 seconds). Proceeding with regular http.',
      );

      // Approach not using websocket.
      const loadActionsPromise = loadAsync<Action>(`${baseUrl}/api/actionPackages`, 'GET');
      const loadRunsPromise = loadAsync<Run>(`${baseUrl}/api/runs`, 'GET');

      const actions = await loadActionsPromise;
      const runs = await loadRunsPromise;

      if (runs.data !== undefined) {
        sortRuns(runs.data);
      }

      this.modelContainer.onModelUpdated(ModelType.ACTIONS, actions);
      this.modelContainer.onModelUpdated(ModelType.RUNS, runs);
    }
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
  const data = await loadAsync(
    `${baseUrl}/api/actions/${actionPackageName}/${actionName}/run`,
    'POST',
    { body: JSON.stringify(args) },
  );
  setLoaded(data);
};

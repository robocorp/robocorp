import { isWindowDefined } from '../lib';
import { IState } from '../treebuild/protocols';

const DEBUG: boolean = false;

interface IVSCode {
  postMessage(message: any): void;
  getState(): any;
  setState(state: any): any;
}

declare global {
  interface Window {
    setVSCodeAPI: (api: IVSCode) => void;
    acquireVsCodeApi: () => IVSCode;
  }
}

export let vscode: IVSCode | undefined; // Loaded in index.htoml
export function setVSCodeAPI(api: IVSCode): void {
  vscode = api;
}

export let windowPlaceholder: any = {};
try {
  windowPlaceholder = window;
} catch (error) {
  // window may not be defined...
}

windowPlaceholder.setVSCodeAPI = setVSCodeAPI;

export function isInVSCode() {
  if (isWindowDefined()) {
    return window.acquireVsCodeApi !== undefined;
  }
  return false;
}

// Note how request/response/event follows the same patterns from the
// DAP (debug adapter protocol).
export interface IRequestMessage {
  type: 'request';
  seq: number;
  command: string;
}

export interface IResponseMessage {
  type: 'response';
  seq: number;
  command: string;
  request_seq: number;
  body?: any;
}

export interface IEventMessage {
  type: 'event';
  seq: number;
  event: string;
  data?: any;
}

export interface ISetContentsRequest {
  type: 'request';
  command: 'setContents';
  initialContents: string;
  runId: string | undefined;
  allRunIdsToLabel: object | undefined;
}

export interface IAppendContentsRequest {
  type: 'request';
  command: 'appendContents';
  appendContents: string;
  runId: string;
}

export interface IUpdateLabelRequest {
  type: 'request';
  command: 'updateLabel';
  runId: string;
  label: string;
}

const msgIdToSeq: any = {};

export function sendRequestToClient(message: IRequestMessage): Promise<any> {
  if (DEBUG) {
    console.log('vscodeComm: sendRequestToClient: ' + JSON.stringify(message));
  }
  let vscodeRef: IVSCode | undefined;
  try {
    vscodeRef = vscode;
  } catch (err) {
    // ignore
  }

  if (vscodeRef) {
    const promise = new Promise((resolve, reject) => {
      msgIdToSeq[message.seq] = resolve;
    });
    vscodeRef.postMessage(message);
    return promise;
  }
  // Unable to send to VSCode because we're not really connected
  // (case when html is opened directly and not through VSCode).
  return new Promise((resolve, reject) => {
    const response: IResponseMessage = {
      type: 'response',
      seq: nextMessageSeq(),
      command: message.command,
      request_seq: message.seq,
      body: undefined,
    };
    resolve(response);
  });
}

export function sendEventToClient(message: IEventMessage): void {
  if (DEBUG) {
    console.log('vscodeComm: send event', message);
  }
  let vscodeRef: IVSCode | undefined;
  try {
    vscodeRef = vscode;
  } catch (err) {
    // ignore
  }

  if (vscodeRef) {
    vscodeRef.postMessage(message);
  }
}

export const eventToHandler: any = {
  output: undefined,
};

export const requestToHandler: any = {
  setContents: undefined,
  appendContents: undefined,
  updateLabel: undefined,
};

// i.e.: Receive message from client
let { addEventListener } = windowPlaceholder;
if (addEventListener === undefined) {
  addEventListener = function (type: any, callback: any) {};
}

addEventListener('message', (event: any) => {
  const msg = event.data;
  if (DEBUG) {
    console.log('vscodeComm: Received message: ' + JSON.stringify(msg));
  }
  if (msg) {
    switch (msg.type) {
      case 'response':
        // Response to something we posted.
        try {
          const responseMsg: IResponseMessage = msg;
          if (
            Object.hasOwn(msgIdToSeq, responseMsg.request_seq) ||
            responseMsg.request_seq in msgIdToSeq
          ) {
            const resolvePromise = msgIdToSeq[responseMsg.request_seq];
            if (resolvePromise) {
              delete msgIdToSeq[responseMsg.request_seq];
              resolvePromise(responseMsg);
              return;
            }
          }
          console.warn('vscodeComm: Unhandled response: ', responseMsg);
        } catch (e) {
          console.error('vscodeComm: Response raised exception:', e);
        }
        break;
      case 'event':
        // Process some event
        try {
          const eventMsg: IEventMessage = msg;
          if (Object.hasOwn(eventToHandler, eventMsg.event) || eventMsg.event in eventToHandler) {
            const handler = eventToHandler[eventMsg.event];
            if (handler) {
              handler(eventMsg);
              return;
            }
          }
          console.warn('vscodeComm: Unhandled event: ', eventMsg);
        } catch (e) {
          console.error('vscodeComm: Event raised exception:', e);
        }
        break;
      case 'request':
        // Process some request
        try {
          const requestMsg: IRequestMessage = msg;
          if (
            Object.hasOwn(requestToHandler, requestMsg.command) ||
            requestMsg.command in requestMsg
          ) {
            const requestHandler = requestToHandler[requestMsg.command];
            if (requestHandler) {
              requestHandler(requestMsg);
              return;
            }
          }
          console.warn('vscodeComm: Unhandled request: ', requestMsg);
        } catch (e) {
          console.error('vscodeComm: Request raised exception:', e);
        }
        break;
    }
  }
});

let _lastMessageId = 0;
export function nextMessageSeq(): number {
  _lastMessageId += 1;
  return _lastMessageId;
}

let _globalState: IState = { filterLevel: 'PASS', runIdToTreeState: {}, runIdLRU: [] };

export function getState(): IState {
  let vscodeRef: IVSCode | undefined;
  try {
    vscodeRef = vscode;
  } catch (err) {}

  if (vscodeRef) {
    let ret: IState = vscodeRef.getState();
    if (!ret) {
      // Initial state.
      ret = _globalState;
    }
    if (ret.filterLevel === undefined) {
      ret.filterLevel = 'PASS';
    }
    if (ret.runIdToTreeState === undefined) {
      ret.runIdToTreeState = {};
    }
    if (!ret.runIdLRU === undefined) {
      ret.runIdLRU = [];
    }
    if (DEBUG) {
      console.log('vscodeComm: getState', JSON.stringify(ret));
    }
    return ret;
  }
  if (DEBUG) {
    console.log('vscodeComm: getState - empty');
  }
  return _globalState;
}

export function setState(state: IState) {
  if (DEBUG) {
    console.log('vscodeComm: setState', JSON.stringify(state));
  }
  let vscodeRef: IVSCode | undefined;
  try {
    vscodeRef = vscode;
  } catch (err) {}

  if (vscodeRef) {
    vscodeRef.setState(state);
  } else {
    _globalState = state;
  }
}

export const onChangeCurrentRunId = (runId: string) => {
  let ev: IEventMessage = {
    type: 'event',
    seq: nextMessageSeq(),
    event: 'onSetCurrentRunId',
  };
  ev['data'] = { runId: runId };
  sendEventToClient(ev);
};

import { debounce } from './debounce';
import { getOpts } from './options';
import { IState } from './protocols';
import { getState, setState } from '../vscode/vscodeComm';

export function collectTreeState(state: IState, runId: string): void {
  let stateForRun = { openNodes: {} };
  if (state.runIdLRU === undefined) {
    state.runIdLRU = [];
  }
  if (state.runIdToTreeState === undefined) {
    state.runIdToTreeState = {};
  } else {
    const oldStateForRun = state.runIdToTreeState[runId];
    if (oldStateForRun) {
      // Try to keep previously opened items (even if
      // they've been filtered out).
      stateForRun = oldStateForRun;
    }
  }

  // TODO: Collect the state

  state.runIdToTreeState[runId] = stateForRun;

  // Don't allow it to grow forever...
  const index = state.runIdLRU.indexOf(runId);
  if (index > -1) {
    state.runIdLRU.splice(index, 1);
  }
  state.runIdLRU.push(runId);

  const MAX_RUNS_SHOWN = 15;
  while (state.runIdLRU.length > MAX_RUNS_SHOWN) {
    const removeRunId = state.runIdLRU.splice(0, 1);
    delete state.runIdToTreeState[removeRunId[0]];
  }
}

export const saveTreeStateLater = debounce(() => {
  saveTreeState();
}, 500);

export function saveTreeState() {
  const opts = getOpts();
  if (opts.state === undefined) {
    opts.state = getState();
  }
  if (opts.runId === undefined) {
    opts.runId = '';
  }
  collectTreeState(opts.state, opts.runId);
  setState(opts.state);
}

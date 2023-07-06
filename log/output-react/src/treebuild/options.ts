import { IOpts } from './protocols';
import { getState } from '../vscode/vscodeComm';

export function createOpts(): IOpts {
  return {
    initialContents: undefined,
    runId: undefined,
    state: undefined,
    onClickReference: undefined,
    appendedContents: [],
    allRunIdsToLabel: {},
  };
}

const _opts: IOpts = createOpts();

export function getOpts(): IOpts {
  if (_opts.state === undefined) {
    _opts.state = getState();
  }
  return _opts;
}

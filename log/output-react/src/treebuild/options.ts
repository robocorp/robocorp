import { IOpts } from './protocols';
import { getState } from './vscodeComm';

const _opts: IOpts = {
  initialContents: undefined,
  runId: undefined,
  state: undefined,
  onClickReference: undefined,
  appendedContents: [],
  allRunIdsToLabel: {},
  showTime: true,
  showExpand: true,
};

export function getOpts(): IOpts {
  if (_opts.state === undefined) {
    _opts.state = getState();
  }
  return _opts;
}

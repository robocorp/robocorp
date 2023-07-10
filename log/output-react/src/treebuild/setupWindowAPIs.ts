import { setAllEntriesWhenPossible, setRunIdsAndLabelWhenPossible } from './effectCallbacks';
import { getOpts } from './options';
import { saveTreeState } from './persistTree';
import { getSampleContents } from './sample';
import { TreeBuilder } from './treeBuilder';
import {
  requestToHandler,
  sendEventToClient,
  nextMessageSeq,
  IEventMessage,
  ISetContentsRequest,
  IAppendContentsRequest,
  IUpdateLabelRequest,
  isInVSCode,
} from '../vscode/vscodeComm';
import { createDefaultRunIdsAndLabel } from '~/lib';

let treeBuilder: TreeBuilder | undefined;

async function rebuildTreeAndStatusesFromOpts(): Promise<void> {
  treeBuilder = new TreeBuilder(getOpts());
  treeBuilder.clearAndInitializeTree();
  await treeBuilder.addInitialContents();
}

function onClickReference(message: any) {
  const ev: IEventMessage = {
    type: 'event',
    seq: nextMessageSeq(),
    event: 'onClickReference',
  };
  ev.data = message;
  sendEventToClient(ev);
}

/**
 * Should be called to set the initial contents of the tree
 * as well as the current run id and label.
 */
export function setContents(msg: ISetContentsRequest): void {
  saveTreeState();
  const opts = getOpts();
  opts.runId = msg.runId;
  opts.initialContents = msg.initialContents;
  if (isInVSCode()) {
    opts.onClickReference = onClickReference;
  }
  opts.appendedContents = [];
  opts.allRunIdsToLabel = msg.allRunIdsToLabel;

  rebuildRunSelection(opts.allRunIdsToLabel, opts.runId);
  rebuildTreeAndStatusesFromOpts();
}

export function appendContents(msg: IAppendContentsRequest): void {
  const opts = getOpts();
  if (opts.runId === msg.runId) {
    opts.appendedContents.push(msg.appendContents);
    if (treeBuilder !== undefined) {
      treeBuilder.onAppendedContents();
    }
  }
}

function rebuildRunSelection(allRunIdsToLabel: object | undefined, runId: string | undefined) {
  const runIdsAndLabel = createDefaultRunIdsAndLabel();
  runIdsAndLabel.currentRunId = runId;
  if (allRunIdsToLabel) {
    for (const [key, value] of Object.entries(allRunIdsToLabel)) {
      runIdsAndLabel.allRunIdsToLabel.set(key, value);
    }
  }

  setRunIdsAndLabelWhenPossible(runIdsAndLabel);
}

export function updateLabel(msg: IUpdateLabelRequest): void {
  const opts = getOpts();
  if (opts.allRunIdsToLabel !== undefined) {
    const all: any = opts.allRunIdsToLabel;
    all[msg.runId] = msg.label;
    rebuildRunSelection(opts.allRunIdsToLabel, opts.runId);
  }
}

function onChangedRun(selectedRun: any) {
  const ev: IEventMessage = {
    type: 'event',
    seq: nextMessageSeq(),
    event: 'onSetCurrentRunId',
  };
  ev.data = { runId: selectedRun };
  sendEventToClient(ev);
}

export function setupScenario(scenario: string) {
  console.log('Setup Scenario');

  const msg: ISetContentsRequest = {
    type: 'request',
    command: 'setContents',
    initialContents: scenario,
    runId: undefined,
    allRunIdsToLabel: undefined,
  };
  setContents(msg);
}

/**
 * Function sets up the globals in requestToHandler and window.
 */
export function setupGlobals() {
  requestToHandler.setContents = setContents;
  requestToHandler.appendContents = appendContents;
  requestToHandler.updateLabel = updateLabel;

  window.onChangedRun = onChangedRun;
  window.setContents = setContents;
  window.getSampleContents = getSampleContents;
  window.setupScenario = setupScenario;
  window.setAllEntriesWhenPossible = setAllEntriesWhenPossible;
}

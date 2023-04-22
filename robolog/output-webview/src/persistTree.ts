import { debounce } from "./debounce";
import { getOpts } from "./options";
import { divById, getDataTreeId } from "./plainDom";
import { IState, ITreeState } from "./protocols";
import { setState } from "./vscodeComm";

function collectLITreeState(state: ITreeState, li: HTMLLIElement) {
    for (let child of li.childNodes) {
        if (child instanceof HTMLDetailsElement) {
            for (let c of child.childNodes) {
                if (c instanceof HTMLUListElement) {
                    collectUlTreeState(state, c);
                }
            }
            if (child.open) {
                state.openNodes[getDataTreeId(li)] = "open";
            } else {
                delete state.openNodes[getDataTreeId(li)];
            }
        }
    }
}

function collectUlTreeState(state: ITreeState, ul: HTMLUListElement) {
    for (let child of ul.childNodes) {
        if (child instanceof HTMLLIElement) {
            collectLITreeState(state, child);
        }
    }
}

export function collectTreeState(state: IState, runId: string): void {
    const mainDiv = divById("mainTree");
    let stateForRun: ITreeState = { "openNodes": {} };
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
    for (let child of mainDiv.childNodes) {
        if (child instanceof HTMLUListElement) {
            collectUlTreeState(stateForRun, child);
        }
    }

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
    collectTreeState(opts.state, opts.runId);
    setState(opts.state);
}

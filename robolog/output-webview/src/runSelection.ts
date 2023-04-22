import { createOption, selectById } from "./plainDom";

export function rebuildRunSelection(allRunIdsToLabel: object | undefined, currentRunId: string) {
    if (allRunIdsToLabel === undefined) {
        return;
    }
    const runSelection = selectById("selectedRun");

    // Mark existing and remove stale.
    const foundRunIdToLabel: Map<string, string> = new Map();
    for (let child of runSelection.childNodes) {
        if (child instanceof HTMLOptionElement) {
            const o: HTMLOptionElement = child;
            const runId = o.value;
            const label = allRunIdsToLabel[runId];
            if (label === undefined) {
                child.remove();
            } else {
                if (o.text !== label) {
                    o.text = label;
                }
                foundRunIdToLabel.set(runId, label);
                const selected = currentRunId == runId;
                o.selected = selected;
            }
        }
    }

    // Add new ones.
    for (const runId of Object.keys(allRunIdsToLabel)) {
        if (runId === undefined) {
            continue;
        }
        const selected = currentRunId == runId;
        if (!foundRunIdToLabel.has(runId)) {
            const opt = createOption();
            const label = allRunIdsToLabel[runId];
            opt.value = runId;
            runSelection.appendChild(opt);
            opt.selected = selected;
            opt.text = label;
            foundRunIdToLabel.set(runId, label);
        }
    }
}

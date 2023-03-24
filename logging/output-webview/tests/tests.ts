import { setContents } from "../src/index";
import { ISetContentsRequest } from "../src/vscodeComm";

export function setupScenario(scenario) {
    console.log("Setup Scenario");

    const msg: ISetContentsRequest = {
        type: "request",
        command: "setContents",
        initialContents: scenario,
        runId: undefined,
        allRunIdsToLabel: undefined,
    };
    setContents(msg);
}

window["setupScenario"] = setupScenario;

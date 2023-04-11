import { IMessage } from "./decoder";

export interface ITreeState {
    openNodes: object;
}

type IRunIdToTreeState = {
    [key: string]: ITreeState;
};

export interface IState {
    filterLevel: IFilterLevel;
    runIdToTreeState: IRunIdToTreeState;
    runIdLRU: string[];
}

export type IFilterLevel = "FAIL" | "WARN" | "PASS" | "NOT RUN";

export interface IOpts {
    runId: string;
    state: IState | undefined;
    onClickReference: Function | undefined;
    allRunIdsToLabel: object;

    // Contains the initial file contents.
    initialContents: string;

    // Contains the contents added afterwards (i.e.:
    // we may add the contents for a session up to a point
    // and then add new messages line by line as it's
    // being tracked afterwards).
    appendedContents: string[];

    showTime: boolean;
    showExpand: boolean;
}

export interface ILiNodesCreated {
    // <li>
    //   <details open>
    //     <summary>
    //       <div class="summaryDiv">
    //          <span class="label">...</span>
    //          <span class="summaryName">...</span>
    //          <span class="summaryInput">...</span>
    //       </div>
    //     </summary>
    //     <div class="detailContainer">
    //       <div class="detailInfo"></div>
    //       <div class="detailInputs"></div>
    //     </div>
    //     <ul>...</ul>
    //   </details>
    // </li>
    li: HTMLLIElement;
    details: HTMLDetailsElement;
    detailContainer: HTMLDivElement;
    summary: HTMLElement;
    summaryDiv: HTMLDivElement;
    summaryName: HTMLElement;
    summaryInput: HTMLElement;
}

export interface IContentAdded {
    ul: HTMLUListElement;
    li: HTMLLIElement;
    details: HTMLDetailsElement;
    detailContainer: HTMLDivElement;
    summary: HTMLElement;
    summaryDiv: HTMLDivElement;
    // note: besides the span below we actually add multiple other span items
    // as we're processing items (i.e.: when we see arguments we may add other spam items
    // and when we see the status we can also add the status).
    summaryName: HTMLElement;
    summaryInput: HTMLElement;

    source: string;
    lineno: number;

    appendContentChild: any;
    decodedMessage: IMessage;

    // Updated when the status or level for an element is set (usually at the end).
    // When a given item finishes updating it'll update its parent accordingly.
    // -1=not run 0 = pass, 1= warn, 2=error
    maxLevelFoundInHierarchy: number;
}

export interface IMessageNode {
    message: IMessage;
    parent: IMessageNode;
}

export interface ITracebackEntry {
    source: string;
    lineno: number;
    method: string;
    lineContent: string;
    variables: Map<string, string>;
}

export class PythonTraceback {
    exceptionMsg: string;
    stack: ITracebackEntry[] = [];
    constructor(exceptionMsg: string) {
        this.exceptionMsg = exceptionMsg;
    }
    pushEntry(source: string, lineno: number, method: string, lineContent: string): void {
        const variables: Map<string, string> = new Map();
        this.stack.push({ source, lineno, method, lineContent, variables });
    }

    pushVar(name: string, type: string, value: string): void {
        const variables = this.stack.at(-1).variables;
        variables.set(`${name} (${type})`, `${value}`);
    }
}

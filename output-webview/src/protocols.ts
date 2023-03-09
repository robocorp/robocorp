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
}

export interface ILiNodesCreated {
    // <li>
    //   <details open>
    //     <summary>
    //          <span></span>
    //     </summary>
    //   </details>
    // </li>
    li: HTMLLIElement;
    details: HTMLDetailsElement;
    summary: HTMLElement;
    summaryDiv: HTMLDivElement;
    span: HTMLElement;
}

export interface IContentAdded {
    // <li>
    //   <details open>
    //     <summary>
    //          <span></span>
    //     </summary>
    //     <ul>
    //     </ul>
    //   </details>
    // </li>
    ul: HTMLUListElement;
    li: HTMLLIElement;
    details: HTMLDetailsElement;
    summary: HTMLElement;
    summaryDiv: HTMLDivElement;
    span: HTMLElement;
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

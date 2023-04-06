import { IContentAdded, ILiNodesCreated, IOpts } from "./protocols";

export function addStatus(current: IContentAdded | ILiNodesCreated, status: string) {
    const span = document.createElement("span");
    span.textContent = status;
    span.classList.add("label");
    span.classList.add(status.replace(" ", "_"));
    current.summaryDiv.insertBefore(span, current.summaryDiv.firstChild);
}

export function addTime(current: IContentAdded, diff: number) {
    const span = document.createElement("span");
    span.textContent = ` (${diff.toFixed(2)}s)`;
    span.classList.add("timeLabel");
    current.summaryDiv.appendChild(span);
}

export function acceptLevel(opts: IOpts, statusLevel: number) {
    switch (opts.state.filterLevel) {
        case "FAIL":
            return statusLevel >= 2;
        case "WARN":
            return statusLevel >= 1;
        case "PASS":
            return statusLevel >= 0;
        case "NOT RUN":
            return true;
    }
}

export function getIntLevelFromStatus(status: string): number {
    switch (status) {
        case "FAIL":
        case "ERROR":
            return 2;
        case "WARN":
            return 1;
        case "NOT RUN":
        case "NOT_RUN":
            return -1;
        case "PASS":
            return 0;
        default:
            return 0;
    }
}

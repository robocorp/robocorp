import { IContentAdded } from "./protocols";

function translateLevel(level: string): string {
    // ERROR = E
    // FAIL = F
    // INFO = I
    // WARN = W
    switch (level) {
        case "E":
            return "ERROR";
        case "F":
            return "FAIL";
        case "W":
            return "WARN";
        case "I":
            return "INFO";

        default:
            return level;
    }
}

export function getIntLevelFromLevelStr(level: string): number {
    switch (level) {
        case "E":
        case "F":
            return 2;
        case "W":
            return 1;
        default:
            return 0;
    }
}

export function addLevel(current: IContentAdded, level: string) {
    const span = document.createElement("span");
    span.textContent = `LOG ${translateLevel(level)}`;
    span.classList.add("label");
    span.classList.add(level.replace(" ", "_"));
    current.summaryDiv.insertBefore(span, current.summaryDiv.firstChild);
}

import { divById } from "./plainDom";

export class SummaryBuilder {
    totalTests: number = 0;
    totalFailures: number = 0;

    clear() {
        this.totalTests = 0;
        this.totalFailures = 0;
        this.updateSummary();
    }

    onTestEndUpdateSummary(msg: any) {
        const status = msg.decoded["status"];
        this.totalTests += 1;
        if (status == "FAIL" || status == "ERROR") {
            this.totalFailures += 1;
        }
        this.updateSummary();
    }

    updateSummary() {
        const totalTestsStr = ("" + this.totalTests).padStart(4);
        const totalFailuresStr = ("" + this.totalFailures).padStart(4);
        const summary = divById("summary");
        summary.textContent = `Total: ${totalTestsStr} Failures: ${totalFailuresStr}`;

        if (this.totalFailures == 0 && this.totalTests == 0) {
            const resultBar: HTMLDivElement = divById("summary");
            resultBar.classList.add("NOT_RUN");
            resultBar.classList.remove("PASS");
            resultBar.classList.remove("FAIL");
        } else if (this.totalFailures == 1) {
            const resultBar: HTMLDivElement = divById("summary");
            resultBar.classList.remove("NOT_RUN");
            resultBar.classList.remove("PASS");
            resultBar.classList.add("FAIL");
        } else if (this.totalFailures == 0 && this.totalTests == 1) {
            const resultBar: HTMLDivElement = divById("summary");
            resultBar.classList.remove("NOT_RUN");
            resultBar.classList.remove("FAIL");
        }
    }
}

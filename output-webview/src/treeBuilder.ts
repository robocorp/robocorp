import { Decoder, iter_decoded_log_format, IMessage } from "./decoder";
import { getIntLevelFromLevelStr, addLevel } from "./handleLevel";
import { acceptLevel, getIntLevelFromStatus, addStatus, addTime } from "./handleStatus";
import { getOpts } from "./options";
import { selectById, divById, createUL, getDataTreeId, createSpan, liMarkedAsHidden } from "./plainDom";
import { IOpts, IContentAdded, IMessageNode } from "./protocols";
import { SummaryBuilder } from "./summaryBuilder";
import { addTreeContent, createLiAndNodesBelow } from "./tree";

/**
 * Helpers to make sure that we only have 1 active tree builder.
 * Whenever we enter a tree builder async-related function it must
 * be checked.
 */
let globalLeaseId: number = 0;
let globalCurrentLease: number = -1;
function obtainNewLease() {
    globalLeaseId += 1;
    globalCurrentLease = globalLeaseId;
    return globalLeaseId;
}

/**
 * A helper class to build the tree.
 *
 * Note that as it adds nodes using async, care must be taken to
 * synchronize operations so that messages are handled in the proper
 * order.
 */
export class TreeBuilder {
    readonly opts: IOpts;
    readonly stack: IContentAdded[] = [];

    // The current element which should have children added to (== stack.at(-1))
    parent: IContentAdded;

    // The current parent and message.
    messageNode: IMessageNode = { "parent": undefined, message: undefined };

    // Current suite name.
    suiteName = "";

    // Current suite source.
    suiteSource = "";

    // A unique incremental id.
    id = 0;

    readonly runId: string;

    readonly summaryBuilder: SummaryBuilder;

    finishedAddingInitialContents: boolean = false;

    lease: number;

    appendedMessagesIndex = -1;

    decoder: Decoder = new Decoder();

    seenSuiteOrTestOrKeyword: boolean = false;

    constructor() {
        this.opts = getOpts();
        this.runId = this.opts.runId;
        this.summaryBuilder = new SummaryBuilder();
        this.lease = obtainNewLease();
        this.resetState();
    }

    resetState() {
        this.seenSuiteOrTestOrKeyword = false;
    }

    /**
     * Should be used to know if this instance is the current one.
     */
    isCurrentTreeBuilder() {
        return this.lease === globalCurrentLease && this.runId == this.opts.runId;
    }

    /**
     * This should be called to clear the initial tree state and
     * get into a clean state.
     */
    clearAndInitializeTree() {
        this.summaryBuilder.clear();
        this.resetState();

        const filterLevelEl: HTMLSelectElement = selectById("filterLevel");
        filterLevelEl.value = this.opts.state.filterLevel;
        const mainDiv = divById("mainTree");
        mainDiv.replaceChildren(); // clear all children

        const rootUl = createUL("ul_root");
        rootUl.classList.add("tree");
        mainDiv.appendChild(rootUl);

        function addToRoot(el: IContentAdded) {
            rootUl.appendChild(el.li);
        }

        this.parent = {
            "ul": undefined,
            "li": undefined,
            "details": undefined,
            "summary": undefined,
            "span": undefined,
            "source": undefined,
            "lineno": undefined,
            "decodedMessage": undefined,
            "appendContentChild": addToRoot,
            "maxLevelFoundInHierarchy": -1,
            "summaryDiv": undefined,
        };
        this.stack.push(this.parent);
    }

    /**
     * Should be used to add the initial contents to the tree. After those are added
     * the contents appended afterwards are handled (in case a running
     * session is being tracked).
     */
    public async addInitialContents(): Promise<void> {
        for (const msg of iter_decoded_log_format(this.opts.initialContents, this.decoder)) {
            if (!this.isCurrentTreeBuilder()) {
                return;
            }
            await this.addOneMessage(msg);
        }
        this.finishedAddingInitialContents = true;
        await this.onAppendedContents();
    }

    /**
     * Used to add to the tree contents appended in real-time.
     */
    public async onAppendedContents(): Promise<void> {
        if (!this.finishedAddingInitialContents) {
            return;
        }
        if (!this.isCurrentTreeBuilder()) {
            return;
        }

        const opts = getOpts();
        while (this.appendedMessagesIndex + 1 < opts.appendedContents.length) {
            this.appendedMessagesIndex += 1;
            const processMsg = opts.appendedContents[this.appendedMessagesIndex];
            for (const msg of iter_decoded_log_format(processMsg, this.decoder)) {
                if (!this.isCurrentTreeBuilder()) {
                    return;
                }
                await this.addOneMessage(msg);
            }
        }
    }

    private async addOneMessage(msg: IMessage): Promise<void> {
        // console.log("#", JSON.stringify(msg));

        if (!this.isCurrentTreeBuilder()) {
            return;
        }
        // Just making sure that the code below is all sync.
        try {
            this.addOneMessageSync(msg);
        } catch (err) {
            console.log("Error: handling message: " + JSON.stringify(msg) + ": " + err + " - " + JSON.stringify(err));
        }
    }

    private addOneMessageSync(msg: IMessage): void {
        let msgType = msg.message_type;
        switch (msgType) {
            // if it's a replay suite/test/keyword, skip it if we've already seen
            // a suit/test/keyword (otherwise, change the replay to the actual
            // type being replayed to have it properly handled).
            case "SS":
            case "ST":
            case "SK":
                this.seenSuiteOrTestOrKeyword = true;
                break;

            case "RS":
                if (this.seenSuiteOrTestOrKeyword) {
                    return;
                }
                msgType = "SS";
                break;
            case "RT":
                if (this.seenSuiteOrTestOrKeyword) {
                    return;
                }
                msgType = "ST";
                break;
            case "RK":
                if (this.seenSuiteOrTestOrKeyword) {
                    return;
                }
                msgType = "SK";
                break;
        }
        this.id += 1;

        switch (msgType) {
            case "SS":
                // start suite

                this.messageNode = { "parent": this.messageNode, "message": msg };
                this.suiteName = msg.decoded["name"] + ".";
                this.suiteSource = msg.decoded["source"];
                // parent = addTreeContent(opts, parent, msg.decoded["name"], msg, true);
                // stack.push(parent);
                break;

            case "ST":
                // start test

                this.messageNode = { "parent": this.messageNode, "message": msg };
                this.parent = addTreeContent(
                    this.opts,
                    this.parent,
                    this.suiteName + msg.decoded["name"],
                    msg,
                    false,
                    this.suiteSource,
                    msg.decoded["lineno"],
                    this.messageNode,
                    this.id.toString()
                );
                this.stack.push(this.parent);
                break;
            case "SK":
                // start keyword
                this.messageNode = { "parent": this.messageNode, "message": msg };
                let libname = msg.decoded["libname"];
                if (libname) {
                    libname += ".";
                }
                this.parent = addTreeContent(
                    this.opts,
                    this.parent,
                    `${msg.decoded["keyword_type"]} - ${libname}${msg.decoded["name"]}`,
                    msg,
                    false,
                    msg.decoded["source"],
                    msg.decoded["lineno"],
                    this.messageNode,
                    this.id.toString()
                );
                this.stack.push(this.parent);
                break;
            case "ES": // end suite
                this.messageNode = this.messageNode.parent;
                this.suiteName = "";
                break;
            case "ET": // end test
                this.messageNode = this.messageNode.parent;
                const currT = this.parent;
                this.stack.pop();
                this.parent = this.stack.at(-1);
                this.onEndUpdateMaxLevelFoundInHierarchyFromStatus(currT, this.parent, msg);
                this.onEndSetStatusOrRemove(this.opts, currT, msg.decoded, this.parent, false);
                this.summaryBuilder.onTestEndUpdateSummary(msg);
                break;
            case "EK": // end keyword
                this.messageNode = this.messageNode.parent;
                let currK = this.parent;
                this.stack.pop();
                this.parent = this.stack.at(-1);
                this.onEndUpdateMaxLevelFoundInHierarchyFromStatus(currK, this.parent, msg);
                this.onEndSetStatusOrRemove(this.opts, currK, msg.decoded, this.parent, true);

                break;
            case "S":
                // Update the start time from the current message.
                const start = msg.decoded["start_time_delta"];
                if (this.parent?.decodedMessage?.decoded) {
                    this.parent.decodedMessage.decoded["time_delta_in_seconds"] = start;
                }
                break;
            case "KA":
                const item: IContentAdded = this.stack.at(-1);
                if (item?.span) {
                    item.span.textContent += ` | ${msg.decoded["argument"]}`;
                }
                break;
            case "L":
            case "LH":
                // A bit different because it's always leaf and based on 'level', not 'status'.
                const level = msg.decoded["level"];
                const iLevel = getIntLevelFromLevelStr(level);
                if (iLevel > this.parent.maxLevelFoundInHierarchy) {
                    this.parent.maxLevelFoundInHierarchy = iLevel;
                    // console.log("set level", parent.decodedMessage, "to", iLevel);
                }
                if (acceptLevel(this.opts, iLevel)) {
                    const logContent = addTreeContent(
                        this.opts,
                        this.parent,
                        msg.decoded["message"],
                        msg,
                        false,
                        undefined,
                        undefined,
                        this.messageNode,
                        this.id.toString()
                    );
                    logContent.maxLevelFoundInHierarchy = iLevel;
                    addLevel(logContent, level);
                }
                break;
        }
    }

    private onEndUpdateMaxLevelFoundInHierarchyFromStatus(current: IContentAdded, parent: IContentAdded, msg: any) {
        const status = msg.decoded["status"];
        const iLevel = getIntLevelFromStatus(status);

        if (iLevel > current.maxLevelFoundInHierarchy) {
            current.maxLevelFoundInHierarchy = iLevel;
        }
        if (current.maxLevelFoundInHierarchy > parent.maxLevelFoundInHierarchy) {
            parent.maxLevelFoundInHierarchy = current.maxLevelFoundInHierarchy;
        }
    }

    /**
     * @param removeIfTooBig if the parent is too big, we may remove the element
     * even if it'd be shown according to the current filter.
     */
    private onEndSetStatusOrRemove(
        opts: IOpts,
        current: IContentAdded,
        endDecodedMsg: object,
        parent: IContentAdded,
        removeIfTooBig: boolean
    ) {
        const status = endDecodedMsg["status"];
        if (acceptLevel(opts, current.maxLevelFoundInHierarchy)) {
            if (removeIfTooBig) {
                if (current.maxLevelFoundInHierarchy <= 0) {
                    // Remove pass/not run and add some placeholder to note it was removed if there
                    // are too many elements under a given parent.
                    const MAX_ELEMENT_COUNT = 50;
                    if (parent.ul.childElementCount > MAX_ELEMENT_COUNT) {
                        const textContent = current.span.textContent;
                        if (textContent && textContent.toLowerCase().includes("iteration")) {
                            const beforeCurrLi: HTMLLIElement = <HTMLLIElement>current.li.previousSibling;
                            const id = getDataTreeId(current.li);
                            current.li.remove();

                            if (liMarkedAsHidden(beforeCurrLi)) {
                                const el = beforeCurrLi.getElementsByClassName("FINAL_SPAN")[0];
                                el.textContent = current.span.textContent;
                            } else {
                                const created = createLiAndNodesBelow(false, id);
                                created.span.textContent = current.span.textContent;

                                created.summary.classList.add("HIDDEN");

                                const span1: HTMLSpanElement = createSpan();
                                span1.setAttribute("role", "button");
                                span1.textContent = "...";
                                span1.classList.add("label");
                                span1.classList.add("HIDDEN");
                                span1.classList.add("inline");

                                created.summaryDiv.appendChild(span1);

                                const span2: HTMLSpanElement = createSpan();
                                span2.setAttribute("role", "button");
                                span2.classList.add("FINAL_SPAN");
                                created.summaryDiv.appendChild(span2);

                                addStatus(created, "HIDDEN");
                                liMarkedAsHidden(created.li, true);
                                parent.ul.appendChild(created.li);
                            }
                            return;
                        }
                    }
                }
            }

            const summary = current.summary;
            addStatus(current, status);

            const startTime: number = current.decodedMessage.decoded["time_delta_in_seconds"];
            if (startTime && startTime >= 0) {
                const endTime: number = endDecodedMsg["time_delta_in_seconds"];
                const diff = endTime - startTime;
                // if (diff > 0) {
                //     console.log("Current: ", JSON.stringify(current.decodedMessage), "end", JSON.stringify(endDecodedMsg));
                //     console.log("Diff: ", diff);
                // }
                addTime(current, diff);
            }
        } else {
            current.li.remove();
        }
    }
}

// Interesting reads:
// https://medium.com/metaphorical-web/javascript-treeview-controls-devil-in-the-details-74c252e00ed8
// https://iamkate.com/code/tree-views/
// https://stackoverflow.com/questions/10813581/can-i-replace-the-expand-icon-of-the-details-element

import { IMessage } from "./decoder";
import { getOpts } from "./options";
import { saveTreeStateLater } from "./persistTree";
import {
    createButton,
    createCollapseSVG,
    createDetails,
    createDiv,
    createExpandSVG,
    createLI,
    createSpan,
    createSummary,
    createUL,
    htmlToElement,
} from "./plainDom";
import { IContentAdded, ILiNodesCreated, IMessageNode, IOpts, ITreeState, PythonTraceback } from "./protocols";

export function addExceptionToNode(nodesCreated: IContentAdded, tb: PythonTraceback) {
    const detailInfo = createDiv();
    detailInfo.classList.add("detailInfo");

    const errorHeader = createDiv();
    errorHeader.classList.add("errorHeader");
    errorHeader.textContent = tb.exceptionMsg;
    detailInfo.appendChild(errorHeader);

    const fullTb: string[] = [];
    for (const tbEntry of tb.stack) {
        let s = tbEntry.source;
        if (s.length > 31) {
            s = `... ${s.substring(27)}`;
        }
        fullTb.push(`File "${s}", line ${tbEntry.lineno}, in ${tbEntry.method}\n`);
        fullTb.push(`    ${tbEntry.lineContent}\n`);
        for (const [name, val] of tbEntry.variables.entries()) {
            fullTb.push(`        💠 ${name} = ${val}\n`);
        }
    }
    const errorEntry = createDiv();
    errorEntry.classList.add("errorDetails");
    errorEntry.style.whiteSpace = "pre";
    errorEntry.textContent = fullTb.join("");
    detailInfo.appendChild(errorEntry);

    nodesCreated.detailContainer.appendChild(detailInfo);

    const detailInputs = createDiv();
    detailInputs.classList.add("detailInputs");
    detailInputs.textContent = " ";
    nodesCreated.detailContainer.appendChild(detailInputs);

    nodesCreated.details.classList.add("parentNode");
}

export function createLiAndNodesBelow(open: boolean, liTreeId: string): ILiNodesCreated {
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

    const li: HTMLLIElement = createLI(liTreeId);
    const details: HTMLDetailsElement = createDetails();

    if (open) {
        details.open = open;
    }

    /* ADD DETAILS INTO LI */

    details.classList.add("NO_CHILDREN");
    li.appendChild(details);

    /* SETUP DETAIL SECTION */

    const detailContainer = createDiv();
    detailContainer.classList.add("detailContainer");

    details.appendChild(detailContainer);

    /* SUMMARY SECTION */

    const summary = createSummary();
    const summaryDiv = createDiv();
    summaryDiv.classList.add("summaryDiv");
    summary.appendChild(summaryDiv);

    const summaryName: HTMLSpanElement = createSpan();
    summaryName.className = "summaryName";
    summaryName.textContent = "[summaryName]";
    summaryDiv.appendChild(summaryName);

    const summaryInput: HTMLSpanElement = createSpan();
    summaryInput.className = "summaryInput emptySummaryInput";
    summaryInput.textContent = "";
    summaryDiv.appendChild(summaryInput);

    details.appendChild(summary);

    const nodesCreated: ILiNodesCreated = {
        li,
        details,
        summary,
        summaryDiv,
        summaryName,
        summaryInput,
        detailContainer,
    };
    return nodesCreated;
}

export function addArgumentsToTreeContent(item: IContentAdded, name: string, type: string, value: string) {
    if (item.summaryInput.classList.contains("emptySummaryInput")) {
        item.summaryInput.textContent = `${name} (${type}) = ${"value"}`;
        item.summaryInput.classList.remove("emptySummaryInput");
    } else {
        item.summaryInput.textContent += `, ${name} (${type}) = ${"value"}`;
    }
}

/**
 * When we add content we initially add it as an item with the NO_CHILDREN class
 * and later we have to remove that class if it has children.
 */
export function addTreeContent(
    opts: IOpts,
    parent: IContentAdded,
    content: string,
    title: string, // tooltip
    decodedMessage: IMessage,
    open: boolean,
    source: string,
    lineno: number,
    messageNode: IMessageNode,
    id: string
): IContentAdded {
    // <li>
    //   <details open>
    //     <summary>
    //          <span></span>
    //     </summary>
    //     <ul>
    //     </ul>
    //   </details>
    // </li>

    const treeState: ITreeState = opts.state.runIdToTreeState[opts.runId];
    const liTreeId = "li_" + id;
    if (treeState) {
        const openNodes = treeState.openNodes;
        if (openNodes) {
            open = openNodes[liTreeId];
        }
    }
    const created = createLiAndNodesBelow(open, liTreeId);
    const li = created.li;
    const details = created.details;
    const detailContainer = created.detailContainer;
    const summary = created.summary;
    const summaryDiv = created.summaryDiv;
    const summaryName = created.summaryName;
    const summaryInput = created.summaryInput;

    if (decodedMessage.message_type === "LH") {
        summaryName.textContent = "";
        const htmlContents = htmlToElement(content);
        summaryName.appendChild(htmlContents);
    } else {
        summaryName.textContent = content;
    }
    if (title) {
        summaryName.title = title;
    }

    if (opts.onClickReference) {
        summaryName.classList.add("span_link");
        summaryName.onclick = (ev) => {
            const scope = [];
            let p: IMessageNode = messageNode.parent;
            while (p !== undefined && p.message !== undefined) {
                scope.push(p.message);
                p = p.parent;
            }

            ev.preventDefault();
            opts.onClickReference({
                source,
                lineno,
                "message": decodedMessage.decoded,
                "messageType": decodedMessage.message_type,
                "scope": scope,
            });
        };
    }

    const ul = createUL("ul_" + id);
    details.appendChild(ul);
    const ret = {
        ul,
        li,
        details,
        detailContainer,
        summary,
        summaryName,
        summaryInput,
        source,
        lineno,
        appendContentChild: undefined,
        decodedMessage,
        maxLevelFoundInHierarchy: -1,
        summaryDiv,
    };
    ret["appendContentChild"] = createUlIfNeededAndAppendChild.bind(ret);
    parent.appendContentChild(ret);
    return ret;
}

let toolbar: HTMLSpanElement = undefined;
let globalCurrMouseOver: IContentAdded = undefined;
function expandOnClick() {
    if (globalCurrMouseOver === undefined) {
        return;
    }
    globalCurrMouseOver.details.open = true;
    for (let details of iterOverUlDetailsElements(globalCurrMouseOver.ul)) {
        if (!details.classList.contains("NO_CHILDREN")) {
            details.open = true;
        }
    }
}

function collapseOnClick() {
    if (globalCurrMouseOver === undefined) {
        return;
    }
    globalCurrMouseOver.details.open = false;
    for (let details of iterOverUlDetailsElements(globalCurrMouseOver.ul)) {
        details.open = false;
    }
}

function* iterOverLiDetailsElements(li: HTMLLIElement): IterableIterator<HTMLDetailsElement> {
    for (let child of li.childNodes) {
        if (child instanceof HTMLDetailsElement) {
            for (let c of child.childNodes) {
                if (c instanceof HTMLUListElement) {
                    for (let details of iterOverUlDetailsElements(c)) {
                        yield details;
                    }
                }
            }
            yield child;
        }
    }
}

function* iterOverUlDetailsElements(ul: HTMLUListElement): IterableIterator<HTMLDetailsElement> {
    for (let child of ul.childNodes) {
        if (child instanceof HTMLLIElement) {
            for (let details of iterOverLiDetailsElements(child)) {
                yield details;
            }
        }
    }
}

function updateOnMouseOver(currMouseOver: IContentAdded) {
    if (toolbar === undefined) {
        toolbar = createDiv();
        toolbar.classList.add("toolbarContainer");

        const expand = createButton();
        expand.appendChild(createExpandSVG());
        expand.onclick = () => {
            expandOnClick();
        };
        expand.classList.add("toolbarButton");

        const collapse = createButton();
        collapse.appendChild(createCollapseSVG());
        collapse.classList.add("toolbarButton");
        collapse.onclick = () => {
            collapseOnClick();
        };
        toolbar.appendChild(collapse);
        toolbar.appendChild(expand);
        return;
    }

    globalCurrMouseOver = currMouseOver;
    currMouseOver.summaryDiv.appendChild(toolbar);
}

function createUlIfNeededAndAppendChild(child: IContentAdded) {
    const bound: IContentAdded = this;
    bound.ul.appendChild(child.li);
    if (bound.details.classList.contains("NO_CHILDREN")) {
        bound.details.classList.remove("NO_CHILDREN");
        // If it can be toggled, track it for changes.
        bound.details.addEventListener("toggle", function () {
            saveTreeStateLater();
        });
        if (getOpts().showExpand) {
            bound.summary.addEventListener("mouseover", (event) => {
                updateOnMouseOver(bound);
            });
        }
    }
}

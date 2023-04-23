function byId<type>(id: string): type {
    return <type>document.getElementById(id);
}

export function divById(id: string): HTMLDivElement {
    return byId<HTMLDivElement>(id);
}

export function selectById(id: string): HTMLSelectElement {
    return byId<HTMLSelectElement>(id);
}

export function createUL(id: string): HTMLUListElement {
    const element = document.createElement("ul");
    element.setAttribute("data-tree-id", id);
    return element;
}

export function createSummary(): HTMLElement {
    return document.createElement("summary");
}

export function createSpan(): HTMLSpanElement {
    return document.createElement("span");
}

export function createOption(): HTMLOptionElement {
    return document.createElement("option");
}

export function createButton(): HTMLButtonElement {
    return document.createElement("button");
}

export function createDiv(): HTMLDivElement {
    return document.createElement("div");
}

export function createLI(id: string): HTMLLIElement {
    const element = document.createElement("li");
    element.setAttribute("data-tree-id", id);
    return element;
}

export function createDetails(): HTMLDetailsElement {
    return document.createElement("details");
}

export function getDataTreeId(element: HTMLLIElement | HTMLUListElement) {
    return element.getAttribute("data-tree-id");
}

export function liMarkedAsHidden(
    element: HTMLLIElement | HTMLUListElement,
    markAsHidden: boolean | undefined = undefined
) {
    if (markAsHidden === undefined) {
        // getter
        return element.getAttribute("data-hidden") === "1";
    }
    // setter
    if (markAsHidden) {
        element.setAttribute("data-hidden", "1");
    } else {
        element.removeAttribute("data-hidden");
    }
}

export function htmlToElement(html) {
    var template = document.createElement("template");
    html = html.trim(); // Never return a text node of whitespace as the result
    template.innerHTML = html;
    return template.content.firstChild;
}

// codicon: https://icon-sets.iconify.design/codicon/expand-all/
export function createExpandSVG() {
    return htmlToElement(
        `<svg xmlns="http://www.w3.org/2000/svg" width="16px" height="16px" preserveAspectRatio="xMidYMid meet" viewBox="0 0 16 16"><g fill="currentColor"><path d="M9 9H4v1h5V9z"/><path d="M7 12V7H6v5h1z"/><path fill-rule="evenodd" d="m5 3l1-1h7l1 1v7l-1 1h-2v2l-1 1H3l-1-1V6l1-1h2V3zm1 2h4l1 1v4h2V3H6v2zm4 1H3v7h7V6z" clip-rule="evenodd"/></g></svg>`
    );
}

// codicon: https://icon-sets.iconify.design/codicon/collapse-all/
export function createCollapseSVG() {
    return htmlToElement(
        `<svg xmlns="http://www.w3.org/2000/svg" width="16px" height="16px" preserveAspectRatio="xMidYMid meet" viewBox="0 0 16 16"><g fill="currentColor"><path d="M9 9H4v1h5V9z"/><path fill-rule="evenodd" d="m5 3l1-1h7l1 1v7l-1 1h-2v2l-1 1H3l-1-1V6l1-1h2V3zm1 2h4l1 1v4h2V3H6v2zm4 1H3v7h7V6z" clip-rule="evenodd"/></g></svg>`
    );
}

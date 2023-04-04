# coding: utf-8
# Note: autogenerated file.
# To regenerate this file use: python -m dev build-output-view.

# The FILE_CONTENTS contains the contents of the files with
# html/javascript code which can be used to visualize the contents of the
# output generated by robocorp-logging (i.e.: the .rfstream files).

FILE_CONTENTS = {'index.html': '<!doctype html><html style="padding: 0 0 0 0; margin: 0 0 0 0; height: 100%"><head><meta charset="utf-8"/><title>Robot Output</title><meta name="viewport" content="width=device-width,initial-scale=1"/></head><body class="vscode-dark" style="padding: 0 0 0 0; margin: 0 0 0 0; height: 100%; display: flex; flex-direction: column"><div style="display: flex"><div class="summaryField" style="flex-grow: 1; white-space: nowrap" id="summary" class="NOT_RUN">Total:&nbsp;&nbsp;&nbsp;&nbsp;Failures:&nbsp;&nbsp;&nbsp;&nbsp;</div><div class="summaryField" style="flex-grow: 1"><div style="display: flex"><span>Filter:&nbsp;</span> <select name="filterLevel" id="filterLevel" style="flex-grow: 1" onchange="window.onChangedFilterLevel()"><option value="FAIL">FAIL</option><option value="WARN">WARN</option><option value="PASS" selected="selected">PASS</option><option value="NOT RUN">NOT RUN</option></select></div></div><div class="summaryField" id="selectRunContainer" style="flex-grow: 2; display: none"><select name="selectedRun" id="selectedRun" onchange="window.onChangedRun()" style="width: 100%"><option value="NO_RUN" selected="selected">No runs available...</option></select></div></div><div id="mainTree" style="white-space: nowrap; overflow: auto; flex-grow: 1"></div><script>(()=>{"use strict";var e={426:(e,n,t)=>{t.d(n,{Z:()=>a});var o=t(645),r=t.n(o)()((function(e){return e[1]}));r.push([e.id,":root {\\n    --fg-color: var(--vscode-editor-foreground, black);\\n    --bg-color: var(--vscode-editor-background, white);\\n    --font-family: var(--vscode-editor-font-family, monospace, courier);\\n    --font-size: var(--vscode-editor-font-size, 14px);\\n    --font-weight: var(--vscode-font-weight);\\n    --menu-background: var(--vscode-menu-background, rgb(235, 235, 235));\\n    --menu-foreground: var(--vscode-menu-foreground, rgb(0, 0, 0));\\n\\n    /* background-color: var(--vscode-editorError-foreground); */\\n    /* background-color: var(--vscode-inputValidation-errorBorder);  high-contrast doesn\'t have a good color */\\n    /* background-color: var(--vscode-testing-iconErrored);  red and green always (not always ideal...) */\\n    --error-background-color: var(--vscode-terminalCommandDecoration-errorBackground, rgb(201, 28, 28));\\n    --error-color: var(--vscode-button-foreground, white);\\n\\n    --hidden-background-color: var(--vscode-foobarcolornotthere, rgb(243, 152, 16));\\n    --hidden-color: var(--vscode-button-foreground, white);\\n\\n    /* background-color: var(--vscode-inputValidation-infoBorder); */\\n    /* background-color: var(--vscode-testing-iconPassed); */\\n    --pass-background-color: var(--vscode-terminalCommandDecoration-successBackground, rgb(36, 47, 202));\\n    --pass-color: var(--vscode-button-foreground, white);\\n\\n    --warn-background-color: var(--vscode-debugConsole-warningForeground, rgb(190, 159, 20));\\n    --warn-color: var(--vscode-button-foreground, white);\\n\\n    --not-run-background-color: var(--vscode-editor-foreground, rgb(102, 102, 102));\\n    --not-run-color: var(--vscode-editor-background, white);\\n\\n    --summary-hover-background-color: var(--vscode-editor-hoverHighlightBackground, rgb(222, 222, 222));\\n\\n    /* \\n    --fg-color: white;\\n    --bg-color: #4b4a4a;\\n    --font-family: \\"Segoe UI\\", Tahoma, Geneva, Verdana, sans-serif; \\n    */\\n}\\n\\n.summaryField {\\n    margin-left: 3px;\\n    margin-right: 3px;\\n}\\n\\nbody {\\n    font-family: var(--font-family);\\n    font-size: var(--font-size);\\n    font-weight: var(--font-weight);\\n    color: var(--fg-color);\\n    background-color: var(--bg-color);\\n}\\n\\n#mainTree {\\n    margin-top: 5px;\\n}\\n\\nul {\\n    list-style-type: none;\\n    padding-inline-start: 0px;\\n    margin-block-start: 0px;\\n}\\n\\ndiv ul:not(:first-child) {\\n    border-left: 1px dotted rgb(141, 141, 141);\\n}\\n\\n.tree li {\\n    display: block;\\n    position: relative;\\n    padding-left: 0px;\\n}\\n\\n.tree ul {\\n    margin-left: 10px;\\n    padding-left: 0;\\n}\\n\\n.toolbarButton {\\n    display: inline;\\n    border-radius: 5px;\\n    background: var(--bg-color);\\n    color: var(--fg-color);\\n    margin-left: 3px;\\n    width: 15px;\\n    height: 15px;\\n    border: 0;\\n    padding: 0;\\n    vertical-align: middle;\\n}\\n\\n.toolbarContainer {\\n    display: inline-block;\\n}\\n\\n.summaryDiv {\\n    display: inline;\\n}\\n\\ndetails > summary {\\n    /* Note: couldn\'t get proper color with the svg approach */\\n    /* list-style-image: url(\\"data:image/svg+xml;utf8,<svg width=\'12px\' height=\'12px\' viewBox=\'0 0 20 20\' xmlns=\'http://www.w3.org/2000/svg\'><g data-name=\'Layer 2\'><g data-name=\'arrow-ios-forward\'><rect width=\'24\' height=\'24\' transform=\'rotate(-90 12 12)\' opacity=\'0\'/><path fill=\'currentColor\' stroke=\'currentColor\' d=\'M10 19a1 1 0 0 1-.64-.23 1 1 0 0 1-.13-1.41L13.71 12 9.39 6.63a1 1 0 0 1 .15-1.41 1 1 0 0 1 1.46.15l4.83 6a1 1 0 0 1 0 1.27l-5 6A1 1 0 0 1 10 19z\'/></g></g></svg>\\"); */\\n    /* list-style-type: \\"⮞ \\"; */\\n    /* list-style-type: \\"⏵\\"; */\\n    list-style-type: \\"+ \\";\\n}\\n\\ndetails[open] > summary {\\n    /* list-style-image: url(\\"data:image/svg+xml;utf8,<svg width=\'12px\' height=\'12px\' viewBox=\'0 0 20 20\' xmlns=\'http://www.w3.org/2000/svg\'><g data-name=\'Layer 2\'><g data-name=\'arrow-ios-downward\'><rect width=\'24\' height=\'24\' opacity=\'0\'/><path fill=\'currentColor\' stroke=\'currentColor\' d=\'M12 16a1 1 0 0 1-.64-.23l-6-5a1 1 0 1 1 1.28-1.54L12 13.71l5.36-4.32a1 1 0 0 1 1.41.15 1 1 0 0 1-.14 1.46l-6 4.83A1 1 0 0 1 12 16z\'/></g></g></svg>\\"); */\\n    /* list-style-type: \\"⮟ \\"; */\\n    /* list-style-type: \\"⏷\\"; */\\n    list-style-type: \\"- \\";\\n}\\n\\n.NO_CHILDREN > summary {\\n    list-style-type: \\"\xa0\xa0\\" !important;\\n}\\n\\nselect {\\n    background-color: var(--menu-background);\\n    color: var(--menu-foreground);\\n}\\n\\nsummary {\\n    padding: 3px;\\n}\\n\\na:link {\\n    color: var(--fg-color);\\n}\\n\\na:visited {\\n    color: var(--fg-color);\\n}\\n\\na:hover {\\n    color: var(--fg-color);\\n}\\n\\na:active {\\n    color: var(--fg-color);\\n}\\n\\n.label {\\n    padding: 2px 2px;\\n    font-size: 0.65em;\\n    letter-spacing: 1px;\\n    white-space: nowrap;\\n    border-radius: 3px;\\n    margin-right: 5px;\\n    font-weight: bold;\\n}\\n\\n.timeLabel {\\n    padding: 2px 2px;\\n    font-size: 0.85em;\\n    letter-spacing: 1px;\\n    white-space: nowrap;\\n    border-radius: 3px;\\n    margin-right: 5px;\\n    font-weight: lighter;\\n}\\n\\n.label.F,\\n.label.E,\\n.label.FAIL,\\n.label.ERROR {\\n    border-radius: 3px;\\n    background-color: var(--error-background-color);\\n    color: var(--error-color);\\n    font-weight: bolder;\\n}\\n\\n.label.PASS,\\n.label.I,\\n.label.INFO {\\n    border-radius: 3px;\\n    background-color: var(--pass-background-color);\\n    color: var(--pass-color);\\n    font-weight: bolder;\\n}\\n\\n.label.W,\\n.label.WARN {\\n    border-radius: 3px;\\n    background-color: var(--warn-background-color);\\n    color: var(--warn-color);\\n    font-weight: bolder;\\n}\\n\\n.label.HIDDEN {\\n    border-radius: 3px;\\n    background-color: var(--hidden-background-color);\\n    color: var(--hidden-color);\\n    font-weight: bolder;\\n}\\n.label.HIDDEN.inline {\\n    margin-left: 5px;\\n}\\n\\nsummary.HIDDEN {\\n    margin-top: 10px;\\n    margin-bottom: 10px;\\n}\\n\\n.label.NOT_RUN {\\n    border-radius: 3px;\\n    background-color: var(--not-run-background-color);\\n    color: var(--not-run-color);\\n    font-weight: bolder;\\n}\\n\\n#summary.FAIL,\\n#summary.ERROR {\\n    border-bottom: 5px solid var(--error-background-color);\\n}\\n\\n#summary.PASS {\\n    border-bottom: 5px solid var(--pass-background-color);\\n}\\n\\n#summary.NOT_RUN {\\n    border-bottom: 5px solid var(--not-run-background-color);\\n}\\n\\n/* .span_link::after {\\n    content: \\" ⮳\\";\\n} */\\n.span_link {\\n    cursor: pointer;\\n    /* text-decoration: underline; */\\n}\\n\\nsummary:hover {\\n    background-color: var(--summary-hover-background-color);\\n}\\n",""]);const a=r},645:e=>{e.exports=function(e){var n=[];return n.toString=function(){return this.map((function(n){var t=e(n);return n[2]?"@media ".concat(n[2]," {").concat(t,"}"):t})).join("")},n.i=function(e,t,o){"string"==typeof e&&(e=[[null,e,""]]);var r={};if(o)for(var a=0;a<this.length;a++){var s=this[a][0];null!=s&&(r[s]=!0)}for(var i=0;i<e.length;i++){var d=[].concat(e[i]);o&&r[d[0]]||(t&&(d[2]?d[2]="".concat(t," and ").concat(d[2]):d[2]=t),n.push(d))}},n}},320:(e,n,t)=>{var o=t(379),r=t.n(o),a=t(426),s={injectType:"singletonStyleTag",insert:"head",singleton:!0};r()(a.Z,s),a.Z.locals},379:(e,n,t)=>{var o,r=function(){var e={};return function(n){if(void 0===e[n]){var t=document.querySelector(n);if(window.HTMLIFrameElement&&t instanceof window.HTMLIFrameElement)try{t=t.contentDocument.head}catch(e){t=null}e[n]=t}return e[n]}}(),a=[];function s(e){for(var n=-1,t=0;t<a.length;t++)if(a[t].identifier===e){n=t;break}return n}function i(e,n){for(var t={},o=[],r=0;r<e.length;r++){var i=e[r],d=n.base?i[0]+n.base:i[0],l=t[d]||0,c="".concat(d," ").concat(l);t[d]=l+1;var u=s(c),m={css:i[1],media:i[2],sourceMap:i[3]};-1!==u?(a[u].references++,a[u].updater(m)):a.push({identifier:c,updater:f(m,n),references:1}),o.push(c)}return o}function d(e){var n=document.createElement("style"),o=e.attributes||{};if(void 0===o.nonce){var a=t.nc;a&&(o.nonce=a)}if(Object.keys(o).forEach((function(e){n.setAttribute(e,o[e])})),"function"==typeof e.insert)e.insert(n);else{var s=r(e.insert||"head");if(!s)throw new Error("Couldn\'t find a style target. This probably means that the value for the \'insert\' parameter is invalid.");s.appendChild(n)}return n}var l,c=(l=[],function(e,n){return l[e]=n,l.filter(Boolean).join("\\n")});function u(e,n,t,o){var r=t?"":o.media?"@media ".concat(o.media," {").concat(o.css,"}"):o.css;if(e.styleSheet)e.styleSheet.cssText=c(n,r);else{var a=document.createTextNode(r),s=e.childNodes;s[n]&&e.removeChild(s[n]),s.length?e.insertBefore(a,s[n]):e.appendChild(a)}}function m(e,n,t){var o=t.css,r=t.media,a=t.sourceMap;if(r?e.setAttribute("media",r):e.removeAttribute("media"),a&&"undefined"!=typeof btoa&&(o+="\\n/*# sourceMappingURL=data:application/json;base64,".concat(btoa(unescape(encodeURIComponent(JSON.stringify(a))))," */")),e.styleSheet)e.styleSheet.cssText=o;else{for(;e.firstChild;)e.removeChild(e.firstChild);e.appendChild(document.createTextNode(o))}}var h=null,p=0;function f(e,n){var t,o,r;if(n.singleton){var a=p++;t=h||(h=d(n)),o=u.bind(null,t,a,!1),r=u.bind(null,t,a,!0)}else t=d(n),o=m.bind(null,t,n),r=function(){!function(e){if(null===e.parentNode)return!1;e.parentNode.removeChild(e)}(t)};return o(e),function(n){if(n){if(n.css===e.css&&n.media===e.media&&n.sourceMap===e.sourceMap)return;o(e=n)}else r()}}e.exports=function(e,n){(n=n||{}).singleton||"boolean"==typeof n.singleton||(n.singleton=(void 0===o&&(o=Boolean(window&&document&&document.all&&!window.atob)),o));var t=i(e=e||[],n);return function(e){if(e=e||[],"[object Array]"===Object.prototype.toString.call(e)){for(var o=0;o<t.length;o++){var r=s(t[o]);a[r].references--}for(var d=i(e,n),l=0;l<t.length;l++){var c=s(t[l]);0===a[c].references&&(a[c].updater(),a.splice(c,1))}t=d}}}},438:(e,n,t)=>{let o;window.setVSCodeAPI=function(e){o=e};let r={};function a(e){let n;try{n=o}catch(e){}n&&n.postMessage(e)}let s={output:void 0},i={setContents:void 0,appendContents:void 0,updateLabel:void 0};window.addEventListener("message",(e=>{let n=e.data;if(n)switch(n.type){case"response":let e=n,t=r[e.request_seq];t&&(delete r[e.request_seq],t(e));break;case"event":let o=s[n.event];o?o(n):console.log("Unhandled event: ",n);break;case"request":let a=i[n.command];a?a(n):console.log("Unhandled request: ",n)}}));let d=0;function l(){return d+=1,d}let c={filterLevel:"PASS",runIdToTreeState:{},runIdLRU:[]},u={initialContents:void 0,runId:void 0,state:void 0,onClickReference:void 0,appendedContents:[],allRunIdsToLabel:{},showTime:!0,showExpand:!0};function m(){return void 0===u.state&&(u.state=function(){let e;try{e=o}catch(e){}if(e){let n=e.getState();return n||(n=c),void 0===n.filterLevel&&(n.filterLevel="PASS"),void 0===n.runIdToTreeState&&(n.runIdToTreeState={}),void 0===!n.runIdLRU&&(n.runIdLRU=[]),n}return c}()),u}function h(e){return document.getElementById(e)}function p(e){return h(e)}function f(e){return h(e)}function v(e){const n=document.createElement("ul");return n.setAttribute("data-tree-id",e),n}function g(){return document.createElement("span")}function b(){return document.createElement("button")}function y(){return document.createElement("div")}function S(e){return e.getAttribute("data-tree-id")}function w(e,n=undefined){if(void 0===n)return"1"===e.getAttribute("data-hidden");n?e.setAttribute("data-hidden","1"):e.removeAttribute("data-hidden")}function N(e){var n=document.createElement("template");return e=e.trim(),n.innerHTML=e,n.content.firstChild}function L(e,n){for(let t of n.childNodes)if(t instanceof HTMLDetailsElement){for(let n of t.childNodes)n instanceof HTMLUListElement&&C(e,n);t.open?e.openNodes[S(n)]="open":delete e.openNodes[S(n)]}}function C(e,n){for(let t of n.childNodes)t instanceof HTMLLIElement&&L(e,t)}const T=((e,n)=>{let t;return function(...e){clearTimeout(t),t=setTimeout((()=>{clearTimeout(t),(()=>{E()})(...e)}),500)}})();function E(){const e=m();!function(e,n){const t=p("mainTree");let o={openNodes:{}};if(void 0===e.runIdLRU&&(e.runIdLRU=[]),void 0===e.runIdToTreeState)e.runIdToTreeState={};else{const t=e.runIdToTreeState[n];t&&(o=t)}for(let e of t.childNodes)e instanceof HTMLUListElement&&C(o,e);e.runIdToTreeState[n]=o;const r=e.runIdLRU.indexOf(n);for(r>-1&&e.runIdLRU.splice(r,1),e.runIdLRU.push(n);e.runIdLRU.length>15;){const n=e.runIdLRU.splice(0,1);delete e.runIdToTreeState[n[0]]}}(e.state,e.runId),function(e){let n;try{n=o}catch(e){}n?n.setState(e):c=e}(e.state)}function I(e,n){if(void 0===e)return;const t=f("selectedRun"),o=new Map;for(let r of t.childNodes)if(r instanceof HTMLOptionElement){const t=r,a=t.value,s=e[a];if(void 0===s)r.remove();else{t.text!==s&&(t.text=s),o.set(a,s);const e=n==a;t.selected=e}}for(const r of Object.keys(e)){if(void 0===r)continue;const a=n==r;if(!o.has(r)){const n=document.createElement("option"),s=e[r];n.value=r,t.appendChild(n),n.selected=a,n.text=s,o.set(r,s)}}}Math.pow(10,8);var K=36e5;var x={dateTimeDelimiter:/[T ]/,timeZoneDelimiter:/[Z ]/i,timezone:/([Z+-].*)$/},M=/^-?(?:(\\d{3})|(\\d{2})(?:-?(\\d{2}))?|W(\\d{2})(?:-?(\\d{1}))?|)$/,k=/^(\\d{2}(?:[.,]\\d*)?)(?::?(\\d{2}(?:[.,]\\d*)?))?(?::?(\\d{2}(?:[.,]\\d*)?))?$/,_=/^([+-])(\\d{2})(?::?(\\d{2}))?$/;function R(e){return e?parseInt(e):1}function A(e){return e&&parseFloat(e.replace(",","."))||0}var D=[31,null,31,30,31,30,31,31,30,31,30,31];function O(e){return e%400==0||e%4==0&&e%100!=0}function F(e,n){const t=e.memo[n];return void 0===t?`<ref not found: ${n}>`:t}function H(e,n){return parseFloat(n)}function U(e,n){return parseInt(n)}function j(e,n){return n}function P(e){const n=[],t=new Map;for(let o of e.split(",")){o=o.trim();let e="oid";if(-1!=o.indexOf(":")&&([o,e]=o.split(":",2)),n.push(o),"oid"===e)t.set(o,F);else if("int"===e)t.set(o,U);else if("float"===e)t.set(o,H);else{if("str"!==e)throw new Error("Unexpected: "+e);t.set(o,j)}}return function(e,o){const r=o.split("|",n.length),a={};for(let o=0;o<r.length;o++){const s=r[o],i=n[o];a[i]=t.get(i)(e,s)}return a}}const B=P("name:oid, suite_id:oid, suite_source:oid, time_delta_in_seconds:float"),z=P("status:oid, time_delta_in_seconds:float"),$=P("name:oid, suite_id:oid, lineno:int, time_delta_in_seconds:float"),V=P("status:oid, message:oid, time_delta_in_seconds:float"),W=P("name:oid, libname:oid, keyword_type:oid, doc:oid, source:oid, lineno:int, time_delta_in_seconds:float"),q=P("status:oid, time_delta_in_seconds:float"),J=P("level:str, message:oid, time_delta_in_seconds:float"),Y={V:function(e,n){return{message:n}},ID:P("part:int, id:str"),I:function(e,n){return JSON.parse(n)},T:function(e,n){return e.initial_time=function(e,n){var t;!function(e,n){if(n.length<1)throw new TypeError("1 argument required, but only "+n.length+" present")}(0,arguments);var o=function(e){if(null===e||!0===e||!1===e)return NaN;var n=Number(e);return isNaN(n)?n:n<0?Math.ceil(n):Math.floor(n)}(null!==(t=null==n?void 0:n.additionalDigits)&&void 0!==t?t:2);if(2!==o&&1!==o&&0!==o)throw new RangeError("additionalDigits must be 0, 1 or 2");if("string"!=typeof e&&"[object String]"!==Object.prototype.toString.call(e))return new Date(NaN);var r,a=function(e){var n,t={},o=e.split(x.dateTimeDelimiter);if(o.length>2)return t;if(/:/.test(o[0])?n=o[0]:(t.date=o[0],n=o[1],x.timeZoneDelimiter.test(t.date)&&(t.date=e.split(x.timeZoneDelimiter)[0],n=e.substr(t.date.length,e.length))),n){var r=x.timezone.exec(n);r?(t.time=n.replace(r[1],""),t.timezone=r[1]):t.time=n}return t}(e);if(a.date){var s=function(e,n){var t=new RegExp("^(?:(\\\\d{4}|[+-]\\\\d{"+(4+n)+"})|(\\\\d{2}|[+-]\\\\d{"+(2+n)+"})$)"),o=e.match(t);if(!o)return{year:NaN,restDateString:""};var r=o[1]?parseInt(o[1]):null,a=o[2]?parseInt(o[2]):null;return{year:null===a?r:100*a,restDateString:e.slice((o[1]||o[2]).length)}}(a.date,o);r=function(e,n){if(null===n)return new Date(NaN);var t=e.match(M);if(!t)return new Date(NaN);var o=!!t[4],r=R(t[1]),a=R(t[2])-1,s=R(t[3]),i=R(t[4]),d=R(t[5])-1;if(o)return function(e,n,t){return n>=1&&n<=53&&t>=0&&t<=6}(0,i,d)?function(e,n,t){var o=new Date(0);o.setUTCFullYear(e,0,4);var r=7*(n-1)+t+1-(o.getUTCDay()||7);return o.setUTCDate(o.getUTCDate()+r),o}(n,i,d):new Date(NaN);var l=new Date(0);return function(e,n,t){return n>=0&&n<=11&&t>=1&&t<=(D[n]||(O(e)?29:28))}(n,a,s)&&function(e,n){return n>=1&&n<=(O(e)?366:365)}(n,r)?(l.setUTCFullYear(n,a,Math.max(r,s)),l):new Date(NaN)}(s.restDateString,s.year)}if(!r||isNaN(r.getTime()))return new Date(NaN);var i,d=r.getTime(),l=0;if(a.time&&(l=function(e){var n=e.match(k);if(!n)return NaN;var t=A(n[1]),o=A(n[2]),r=A(n[3]);return function(e,n,t){return 24===e?0===n&&0===t:t>=0&&t<60&&n>=0&&n<60&&e>=0&&e<25}(t,o,r)?t*K+6e4*o+1e3*r:NaN}(a.time),isNaN(l)))return new Date(NaN);if(!a.timezone){var c=new Date(d+l),u=new Date(0);return u.setFullYear(c.getUTCFullYear(),c.getUTCMonth(),c.getUTCDate()),u.setHours(c.getUTCHours(),c.getUTCMinutes(),c.getUTCSeconds(),c.getUTCMilliseconds()),u}return i=function(e){if("Z"===e)return 0;var n=e.match(_);if(!n)return 0;var t="+"===n[1]?-1:1,o=parseInt(n[2]),r=n[3]&&parseInt(n[3])||0;return function(e,n){return n>=0&&n<=59}(0,r)?t*(o*K+6e4*r):NaN}(a.timezone),isNaN(i)?new Date(NaN):new Date(d+l+i)}(n),{time:n}},M:function(e,n){var t,o;const r=G(n,":");if(r){[t,o]=r;try{o=JSON.parse(o)}catch(e){return console.log("Error parsing json: "+o),console.log(e),null}e.memo[t]=o}return null},SS:B,RS:B,ES:z,ST:$,RT:$,ET:V,SK:W,RK:W,EK:q,KA:P("argument:oid"),L:J,LH:J,AS:P("assign:oid"),TG:P("tag:oid"),S:P("start_time_delta:float")};class Z{constructor(){this.memo={},this.initial_time=null,this.level=0,this.ident=""}decode_message_type(e,n){return(0,Y[e])(this,n)}}function G(e,n){const t=e.indexOf(n);if(t>0)return[e.substring(0,t),e.substring(t+1)]}function*Q(e,n){var t,o,r;for(let a of e.split(/\\r?\\n/))if(a=a.trim(),a){const e=G(a," ");if(e&&([r,o]=e,t=n.decode_message_type(r,o))){const e={message_type:r,decoded:t};yield e}}}function X(e,n){const t=document.createElement("span");t.textContent=n,t.classList.add("label"),t.classList.add(n.replace(" ","_")),e.summaryDiv.insertBefore(t,e.summaryDiv.firstChild)}function ee(e,n){switch(e.state.filterLevel){case"FAIL":return n>=2;case"WARN":return n>=1;case"PASS":return n>=0;case"NOT RUN":return!0}}class ne{constructor(){this.totalTests=0,this.totalFailures=0}clear(){this.totalTests=0,this.totalFailures=0,this.updateSummary()}onTestEndUpdateSummary(e){const n=e.decoded.status;this.totalTests+=1,"FAIL"!=n&&"ERROR"!=n||(this.totalFailures+=1),this.updateSummary()}updateSummary(){const e=p("summary");if(!e)return;const n=(""+this.totalTests).padStart(4),t=(""+this.totalFailures).padStart(4);if(e.textContent=`Total: ${n} Failures: ${t}`,0==this.totalFailures&&0==this.totalTests){const e=p("summary");e.classList.add("NOT_RUN"),e.classList.remove("PASS"),e.classList.remove("FAIL")}else if(1==this.totalFailures){const e=p("summary");e.classList.remove("NOT_RUN"),e.classList.remove("PASS"),e.classList.add("FAIL")}else if(0==this.totalFailures&&1==this.totalTests){const e=p("summary");e.classList.remove("NOT_RUN"),e.classList.remove("FAIL")}}}function te(e,n){const t=function(e){const n=document.createElement("li");return n.setAttribute("data-tree-id",e),n}(n),o=document.createElement("details");e&&(o.open=e),o.classList.add("NO_CHILDREN"),t.appendChild(o);const r=y();r.classList.add("detailContainer");const a=y();a.classList.add("detailInfo"),a.innerHTML=\'<div class="errorHeader">TypeError: NoneType object is not subscriptable</div><div class="errorDetails">set_value_by_xpath(f//input[@ng-reflect-name="{name}"]\\\',person[key])<br>challenge.py, line 32</div>\',r.appendChild(a);const s=y();s.classList.add("detailInputs"),s.textContent=" ",r.appendChild(s),o.appendChild(r);const i=document.createElement("summary"),d=y();d.classList.add("summaryDiv"),i.appendChild(d);const l=g();l.className="summaryName",l.textContent="[summaryName]",d.appendChild(l);const c=g();return c.className="summaryInput",c.textContent="—",d.appendChild(c),o.appendChild(i),{li:t,details:o,summary:i,summaryDiv:d,detailInputs:s,summaryName:l,summaryInput:c}}function oe(e,n,t,o,r,a,s,i,d){const l=e.state.runIdToTreeState[e.runId],c="li_"+d;if(l){const e=l.openNodes;e&&(r=e[c])}const u=te(r,c),m=u.li,h=u.details,p=u.summary,f=u.summaryDiv,g=u.summaryName,b=u.summaryInput;if("LH"===o.message_type){const e=N(t);g.appendChild(e)}else g.textContent=t;e.onClickReference&&(g.classList.add("span_link"),g.onclick=n=>{const t=[];let r=i.parent;for(;void 0!==r&&void 0!==r.message;)t.push(r.message),r=r.parent;n.preventDefault(),e.onClickReference({source:a,lineno:s,message:o.decoded,messageType:o.message_type,scope:t})});const y=v("ul_"+d);h.appendChild(y);const S={ul:y,li:m,details:h,summary:p,summaryName:g,summaryInput:b,source:a,lineno:s,appendContentChild:void 0,decodedMessage:o,maxLevelFoundInHierarchy:-1,summaryDiv:f};return S.appendContentChild=de.bind(S),n.appendContentChild(S),S}let re,ae;function*se(e){for(let n of e.childNodes)if(n instanceof HTMLDetailsElement){for(let e of n.childNodes)if(e instanceof HTMLUListElement)for(let n of ie(e))yield n;yield n}}function*ie(e){for(let n of e.childNodes)if(n instanceof HTMLLIElement)for(let e of se(n))yield e}function de(e){const n=this;n.ul.appendChild(e.li),n.details.classList.contains("NO_CHILDREN")&&(n.details.classList.remove("NO_CHILDREN"),n.details.addEventListener("toggle",(function(){T()})),m().showExpand&&n.summary.addEventListener("mouseover",(e=>{!function(e){if(void 0===re){re=y(),re.classList.add("toolbarContainer");const e=b();e.appendChild(N(\'<svg xmlns="http://www.w3.org/2000/svg" width="16px" height="16px" preserveAspectRatio="xMidYMid meet" viewBox="0 0 16 16"><g fill="currentColor"><path d="M9 9H4v1h5V9z"/><path d="M7 12V7H6v5h1z"/><path fill-rule="evenodd" d="m5 3l1-1h7l1 1v7l-1 1h-2v2l-1 1H3l-1-1V6l1-1h2V3zm1 2h4l1 1v4h2V3H6v2zm4 1H3v7h7V6z" clip-rule="evenodd"/></g></svg>\')),e.onclick=()=>{!function(){if(void 0!==ae){ae.details.open=!0;for(let e of ie(ae.ul))e.classList.contains("NO_CHILDREN")||(e.open=!0)}}()},e.classList.add("toolbarButton");const n=b();return n.appendChild(N(\'<svg xmlns="http://www.w3.org/2000/svg" width="16px" height="16px" preserveAspectRatio="xMidYMid meet" viewBox="0 0 16 16"><g fill="currentColor"><path d="M9 9H4v1h5V9z"/><path fill-rule="evenodd" d="m5 3l1-1h7l1 1v7l-1 1h-2v2l-1 1H3l-1-1V6l1-1h2V3zm1 2h4l1 1v4h2V3H6v2zm4 1H3v7h7V6z" clip-rule="evenodd"/></g></svg>\')),n.classList.add("toolbarButton"),n.onclick=()=>{!function(){if(void 0!==ae){ae.details.open=!1;for(let e of ie(ae.ul))e.open=!1}}()},re.appendChild(n),void re.appendChild(e)}ae=e,e.summaryDiv.appendChild(re)}(n)})))}var le=function(e,n,t,o){return new(t||(t=Promise))((function(r,a){function s(e){try{d(o.next(e))}catch(e){a(e)}}function i(e){try{d(o.throw(e))}catch(e){a(e)}}function d(e){var n;e.done?r(e.value):(n=e.value,n instanceof t?n:new t((function(e){e(n)}))).then(s,i)}d((o=o.apply(e,n||[])).next())}))};let ce=0,ue=-1;class me{constructor(){this.stack=[],this.messageNode={parent:void 0,message:void 0},this.suiteName="",this.suiteSource="",this.id=0,this.finishedAddingInitialContents=!1,this.appendedMessagesIndex=-1,this.decoder=new Z,this.seenSuiteOrTestOrKeyword=!1,this.opts=m(),this.runId=this.opts.runId,this.summaryBuilder=new ne,this.lease=(ce+=1,ue=ce,ce),this.resetState()}resetState(){this.seenSuiteOrTestOrKeyword=!1}isCurrentTreeBuilder(){return this.lease===ue&&this.runId==this.opts.runId}clearAndInitializeTree(){this.summaryBuilder.clear(),this.resetState();const e=f("filterLevel");e&&(e.value=this.opts.state.filterLevel);const n=p("mainTree");n.replaceChildren();const t=v("ul_root");t.classList.add("tree"),n.appendChild(t),this.parent={ul:void 0,li:void 0,details:void 0,summary:void 0,summaryName:void 0,summaryInput:void 0,source:void 0,lineno:void 0,decodedMessage:void 0,appendContentChild:function(e){t.appendChild(e.li)},maxLevelFoundInHierarchy:-1,summaryDiv:void 0},this.stack.push(this.parent)}addInitialContents(){return le(this,void 0,void 0,(function*(){for(const e of Q(this.opts.initialContents,this.decoder)){if(!this.isCurrentTreeBuilder())return;yield this.addOneMessage(e)}this.finishedAddingInitialContents=!0,yield this.onAppendedContents()}))}onAppendedContents(){return le(this,void 0,void 0,(function*(){if(!this.finishedAddingInitialContents)return;if(!this.isCurrentTreeBuilder())return;const e=m();for(;this.appendedMessagesIndex+1<e.appendedContents.length;){this.appendedMessagesIndex+=1;const n=e.appendedContents[this.appendedMessagesIndex];for(const e of Q(n,this.decoder)){if(!this.isCurrentTreeBuilder())return;yield this.addOneMessage(e)}}}))}addOneMessage(e){return le(this,void 0,void 0,(function*(){if(this.isCurrentTreeBuilder())try{this.addOneMessageSync(e)}catch(n){console.log("Error: handling message: "+JSON.stringify(e)+": "+n+" - "+JSON.stringify(n))}}))}addOneMessageSync(e){var n,t;let o=e.message_type;switch(o){case"SS":case"ST":case"SK":this.seenSuiteOrTestOrKeyword=!0;break;case"RS":if(this.seenSuiteOrTestOrKeyword)return;o="SS";break;case"RT":if(this.seenSuiteOrTestOrKeyword)return;o="ST";break;case"RK":if(this.seenSuiteOrTestOrKeyword)return;o="SK"}switch(this.id+=1,o){case"SS":this.messageNode={parent:this.messageNode,message:e},this.suiteName=e.decoded.name+".",this.suiteSource=e.decoded.source;break;case"ST":this.messageNode={parent:this.messageNode,message:e},this.parent=oe(this.opts,this.parent,this.suiteName+e.decoded.name,e,!1,this.suiteSource,e.decoded.lineno,this.messageNode,this.id.toString()),this.stack.push(this.parent);break;case"SK":this.messageNode={parent:this.messageNode,message:e};let o=e.decoded.libname;o&&(o+="."),this.parent=oe(this.opts,this.parent,`${o}${e.decoded.name}`,e,!1,e.decoded.source,e.decoded.lineno,this.messageNode,this.id.toString()),this.stack.push(this.parent);break;case"ES":this.messageNode=this.messageNode.parent,this.suiteName="";break;case"ET":this.messageNode=this.messageNode.parent;const r=this.parent;this.stack.pop(),this.parent=this.stack.at(-1),this.onEndUpdateMaxLevelFoundInHierarchyFromStatus(r,this.parent,e),this.onEndSetStatusOrRemove(this.opts,r,e.decoded,this.parent,!1),this.summaryBuilder.onTestEndUpdateSummary(e),"ERROR"===e.decoded.status?(console.log("END KEYWORD",this.opts,r,e.decoded,this.parent,!0),r.details.open=!0,r.details.classList.add("errorParent")):r.details.classList.add("passParent"),0===r.ul.children.length?r.details.classList.add("leafNode"):r.details.classList.add("parentNode");break;case"EK":this.messageNode=this.messageNode.parent;let a=this.parent;this.stack.pop(),this.parent=this.stack.at(-1),this.onEndUpdateMaxLevelFoundInHierarchyFromStatus(a,this.parent,e),this.onEndSetStatusOrRemove(this.opts,a,e.decoded,this.parent,!0),"ERROR"===e.decoded.status?(a.details.open=!0,a.details.classList.add("errorParent")):a.details.classList.add("passParent"),0===a.ul.children.length?a.details.classList.add("leafNode"):a.details.classList.add("parentNode");break;case"S":const s=e.decoded.start_time_delta;(null===(t=null===(n=this.parent)||void 0===n?void 0:n.decodedMessage)||void 0===t?void 0:t.decoded)&&(this.parent.decodedMessage.decoded.time_delta_in_seconds=s);break;case"KA":const i=this.stack.at(-1);i.summaryInput.textContent.endsWith("—")?i.summaryInput.textContent=`${e.decoded.argument}`:i.summaryInput.textContent+=`, ${e.decoded.argument}`;break;case"L":case"LH":const d=e.decoded.level,l=function(e){switch(e){case"E":case"F":return 2;case"W":return 1;default:return 0}}(d);if(l>this.parent.maxLevelFoundInHierarchy&&(this.parent.maxLevelFoundInHierarchy=l),ee(this.opts,l)){const n=oe(this.opts,this.parent,e.decoded.message,e,!1,void 0,void 0,this.messageNode,this.id.toString());n.maxLevelFoundInHierarchy=l,function(e,n){const t=document.createElement("span");t.textContent=`LOG ${function(e){switch(e){case"E":return"ERROR";case"F":return"FAIL";case"W":return"WARN";case"I":return"INFO";default:return e}}(n)}`,t.classList.add("label"),t.classList.add(n.replace(" ","_")),e.summaryDiv.insertBefore(t,e.summaryDiv.firstChild)}(n,d),l>=2?n.details.classList.add("errorParent"):n.details.classList.add("passParent"),n.details.classList.add("leafNode")}}}onEndUpdateMaxLevelFoundInHierarchyFromStatus(e,n,t){const o=function(e){switch(e){case"FAIL":case"ERROR":return 2;case"WARN":return 1;case"NOT RUN":case"NOT_RUN":return-1;default:return 0}}(t.decoded.status);o>e.maxLevelFoundInHierarchy&&(e.maxLevelFoundInHierarchy=o),e.maxLevelFoundInHierarchy>n.maxLevelFoundInHierarchy&&(n.maxLevelFoundInHierarchy=e.maxLevelFoundInHierarchy)}onEndSetStatusOrRemove(e,n,t,o,r){const a=t.status;if(ee(e,n.maxLevelFoundInHierarchy)){if(r&&n.maxLevelFoundInHierarchy<=0){const e=50;if(o.ul.childElementCount>e){const e=n.summaryName.textContent;if(e&&e.toLowerCase().includes("iteration")){const e=n.li.previousSibling,t=S(n.li);if(n.li.remove(),w(e))e.getElementsByClassName("FINAL_SPAN")[0].textContent=n.summaryName.textContent;else{const e=te(!1,t);e.summaryName.textContent=n.summaryName.textContent,e.summary.classList.add("HIDDEN");const r=g();r.setAttribute("role","button"),r.textContent="...",r.classList.add("label"),r.classList.add("HIDDEN"),r.classList.add("inline"),e.summaryDiv.appendChild(r);const a=g();a.setAttribute("role","button"),a.classList.add("FINAL_SPAN"),e.summaryDiv.appendChild(a),X(e,"HIDDEN"),w(e.li,!0),o.ul.appendChild(e.li)}return}}}if(n.summary,X(n,a),this.opts.showTime){const e=n.decodedMessage.decoded.time_delta_in_seconds;e&&e>=0&&function(e,n){const t=document.createElement("span");t.textContent=` (${n.toFixed(2)}s)`,t.classList.add("timeLabel"),e.summaryDiv.appendChild(t)}(n,t.time_delta_in_seconds-e)}}else n.li.remove()}}var he=function(e,n,t,o){return new(t||(t=Promise))((function(r,a){function s(e){try{d(o.next(e))}catch(e){a(e)}}function i(e){try{d(o.throw(e))}catch(e){a(e)}}function d(e){var n;e.done?r(e.value):(n=e.value,n instanceof t?n:new t((function(e){e(n)}))).then(s,i)}d((o=o.apply(e,n||[])).next())}))};let pe;function fe(){return he(this,void 0,void 0,(function*(){pe=new me,pe.clearAndInitializeTree(),yield pe.addInitialContents()}))}function ve(e){let n={type:"event",seq:l(),event:"onClickReference"};n.data=e,a(n)}function ge(e){E();const n=m();n.runId=e.runId,n.initialContents=e.initialContents,void 0!==o&&(n.onClickReference=ve),n.appendedContents=[],n.allRunIdsToLabel=e.allRunIdsToLabel,I(n.allRunIdsToLabel,n.runId),fe()}t(320),i.setContents=ge,i.appendContents=function(e){const n=m();n.runId===e.runId&&(n.appendedContents.push(e.appendContents),void 0!==pe&&pe.onAppendedContents())},i.updateLabel=function(e){const n=m();n.allRunIdsToLabel[e.runId]=e.label,I(n.allRunIdsToLabel,n.runId)},window.onChangedRun=function(){const e=f("selectedRun").value;let n={type:"event",seq:l(),event:"onSetCurrentRunId"};n.data={runId:e},a(n)},window.onChangedFilterLevel=function(){!function(e){const n=m();n.state.filterLevel!==e&&(n.state.filterLevel=e,E(),fe())}(f("filterLevel").value)},window.setContents=ge,window.setShowTime=function(e){m().showTime=e},window.setShowExpand=function(e){m().showExpand=e},window.getSampleContents=function(){return JSON.parse(\'"V 1\\\\nI \\\\"sys.platform=win32\\\\"\\\\nI \\\\"python=3.7.6 (default, Jan  8 2020, 20:23:39) [MSC v.1916 64 bit (AMD64)]\\\\"\\\\nI \\\\"robot=5.1a3.dev1\\\\"\\\\nT 2022-10-19T09:48:34.018\\\\nM a:\\\\"Robot1\\\\"\\\\nM b:\\\\"s1\\\\"\\\\nM c:\\\\"C:\\\\\\\\\\\\\\\\Users\\\\\\\\\\\\\\\\fabio\\\\\\\\\\\\\\\\AppData\\\\\\\\\\\\\\\\Local\\\\\\\\\\\\\\\\Temp\\\\\\\\\\\\\\\\pytest-of-fabio\\\\\\\\\\\\\\\\pytest-421\\\\\\\\\\\\\\\\test_robot_out_stream0\\\\\\\\\\\\\\\\test_robot_out_stream\\\\\\\\\\\\\\\\robot1.robot\\\\"\\\\nSS a|b|c|0.035\\\\nM d:\\\\"Simple Task\\\\"\\\\nM e:\\\\"s1-t1\\\\"\\\\nST d|e|16|0.036\\\\nM f:\\\\"First keyword\\\\"\\\\nM g:\\\\"\\\\"\\\\nM h:\\\\"KEYWORD\\\\"\\\\nSK f|g|h|g|c|17|0.036\\\\nM i:\\\\"No Operation\\\\"\\\\nM j:\\\\"BuiltIn\\\\"\\\\nM k:\\\\"Does absolutely nothing.\\\\"\\\\nSK i|j|h|k|c|8|0.037\\\\nM l:\\\\"PASS\\\\"\\\\nEK l|0.037\\\\nM m:\\\\"Log\\\\"\\\\nM n:\\\\"Logs the given message with the given level.\\\\"\\\\nSK m|j|h|n|c|10|0.037\\\\nM o:\\\\"Some warning message\\\\"\\\\nKA o\\\\nM p:\\\\"level=WARN\\\\"\\\\nKA p\\\\nEK l|0.046\\\\nM q:\\\\"Another keyword\\\\"\\\\nM r:\\\\"another\\\\"\\\\nSK q|r|h|g|c|11|0.047\\\\nM s:\\\\"C:\\\\\\\\\\\\\\\\Users\\\\\\\\\\\\\\\\fabio\\\\\\\\\\\\\\\\AppData\\\\\\\\\\\\\\\\Local\\\\\\\\\\\\\\\\Temp\\\\\\\\\\\\\\\\pytest-of-fabio\\\\\\\\\\\\\\\\pytest-421\\\\\\\\\\\\\\\\test_robot_out_stream0\\\\\\\\\\\\\\\\test_robot_out_stream\\\\\\\\\\\\\\\\another.robot\\\\"\\\\nSK i|j|h|k|s|3|0.047\\\\nEK l|0.047\\\\nEK l|0.047\\\\nM t:\\\\"Another in sub keyword\\\\"\\\\nM u:\\\\"another_sub\\\\"\\\\nSK t|u|h|g|c|12|0.047\\\\nM v:\\\\"C:\\\\\\\\\\\\\\\\Users\\\\\\\\\\\\\\\\fabio\\\\\\\\\\\\\\\\AppData\\\\\\\\\\\\\\\\Local\\\\\\\\\\\\\\\\Temp\\\\\\\\\\\\\\\\pytest-of-fabio\\\\\\\\\\\\\\\\pytest-421\\\\\\\\\\\\\\\\test_robot_out_stream0\\\\\\\\\\\\\\\\test_robot_out_stream\\\\\\\\\\\\\\\\sub\\\\\\\\\\\\\\\\another_sub.robot\\\\"\\\\nSK i|j|h|k|v|6|0.048\\\\nEK l|0.048\\\\nSK m|j|h|n|v|7|0.048\\\\nM w:\\\\"Some error message\\\\"\\\\nKA w\\\\nM x:\\\\"level=ERROR\\\\"\\\\nKA x\\\\nEK l|0.049\\\\nEK l|0.049\\\\nEK l|0.049\\\\nSK m|j|h|n|c|18|0.049\\\\nM y:\\\\"Some <data &encode <\\/script>\\\\"\\\\nKA y\\\\nEK l|0.049\\\\nM z:\\\\"Create Dictionary\\\\"\\\\nM A:\\\\"Creates and returns a dictionary based on the given ``items``.\\\\"\\\\nSK z|j|h|A|c|19|0.049\\\\nM B:\\\\"a=1\\\\"\\\\nKA B\\\\nM C:\\\\"b=1\\\\"\\\\nKA C\\\\nEK l|0.05\\\\nSK m|j|h|n|c|20|0.05\\\\nM D:\\\\"${dct}\\\\"\\\\nKA D\\\\nEK l|0.051\\\\nET l|g|0.051\\\\nM E:\\\\"Check 1\\\\"\\\\nM F:\\\\"s1-t2\\\\"\\\\nST E|F|22|0.051\\\\nSK f|g|h|g|c|23|0.051\\\\nSK i|j|h|k|c|8|0.052\\\\nEK l|0.052\\\\nSK m|j|h|n|c|10|0.052\\\\nKA o\\\\nKA p\\\\nEK l|0.052\\\\nSK q|r|h|g|c|11|0.053\\\\nSK i|j|h|k|s|3|0.053\\\\nEK l|0.053\\\\nEK l|0.053\\\\nSK t|u|h|g|c|12|0.053\\\\nSK i|j|h|k|v|6|0.054\\\\nEK l|0.054\\\\nSK m|j|h|n|v|7|0.054\\\\nKA w\\\\nKA x\\\\nEK l|0.054\\\\nEK l|0.055\\\\nEK l|0.055\\\\nM G:\\\\"${counter} IN RANGE [ 0 | 3 ]\\\\"\\\\nM H:\\\\"FOR\\\\"\\\\nSK G|g|H|g|c|25|0.055\\\\nM I:\\\\"${counter} = 0\\\\"\\\\nM J:\\\\"ITERATION\\\\"\\\\nSK I|g|J|g|c|25|0.055\\\\nM K:\\\\"${counter} == 2\\\\"\\\\nM L:\\\\"IF\\\\"\\\\nSK K|g|L|g|c|26|0.055\\\\nM M:\\\\"Fail\\\\"\\\\nM N:\\\\"Fails the test with the given message and optionally alters its tags.\\\\"\\\\nSK M|j|h|N|c|27|0.056\\\\nM O:\\\\"Failed execution for some reason...\\\\"\\\\nKA O\\\\nM P:\\\\"NOT RUN\\\\"\\\\nEK P|0.056\\\\nEK P|0.056\\\\nSK m|j|h|n|c|29|0.056\\\\nM Q:\\\\"${counter}\\\\"\\\\nKA Q\\\\nEK l|0.056\\\\nEK l|0.057\\\\nM R:\\\\"${counter} = 1\\\\"\\\\nSK R|g|J|g|c|25|0.057\\\\nSK K|g|L|g|c|26|0.057\\\\nSK M|j|h|N|c|27|0.057\\\\nKA O\\\\nEK P|0.057\\\\nEK P|0.057\\\\nSK m|j|h|n|c|29|0.058\\\\nKA Q\\\\nEK l|0.058\\\\nEK l|0.058\\\\nM S:\\\\"${counter} = 2\\\\"\\\\nSK S|g|J|g|c|25|0.058\\\\nSK K|g|L|g|c|26|0.058\\\\nSK M|j|h|N|c|27|0.059\\\\nKA O\\\\nM T:\\\\"FAIL\\\\"\\\\nEK T|0.059\\\\nEK T|0.059\\\\nSK m|j|h|n|c|29|0.059\\\\nKA Q\\\\nEK P|0.059\\\\nEK T|0.06\\\\nEK T|0.06\\\\nET T|O|0.06\\\\nM U:\\\\"Check 2\\\\"\\\\nM V:\\\\"s1-t3\\\\"\\\\nST U|V|32|0.06\\\\nM W:\\\\"Set Variable\\\\"\\\\nM X:\\\\"Returns the given values which can then be assigned to a variables.\\\\"\\\\nSK W|j|h|X|c|33|0.061\\\\nM Y:\\\\"3\\\\"\\\\nKA Y\\\\nEK l|0.061\\\\nM Z:\\\\"${counter} <= 2\\\\"\\\\nM 0:\\\\"WHILE\\\\"\\\\nSK Z|g|0|g|c|34|0.061\\\\nSK g|g|J|g|c|34|0.062\\\\nM 1:\\\\"Evaluate\\\\"\\\\nM 2:\\\\"Evaluates the given expression in Python and returns the result.\\\\"\\\\nSK 1|j|h|2|c|35|0.062\\\\nM 4:\\\\"$counter-1\\\\"\\\\nKA 4\\\\nEK P|0.062\\\\nSK m|j|h|n|c|36|0.062\\\\nM 5:\\\\"Current counter: ${counter}\\\\"\\\\nKA 5\\\\nKA p\\\\nEK P|0.062\\\\nEK P|0.062\\\\nEK P|0.063\\\\nET l|g|0.063\\\\nM 6:\\\\"Check 3\\\\"\\\\nM 7:\\\\"s1-t4\\\\"\\\\nST 6|7|39|0.064\\\\nM 8:\\\\"TRY\\\\"\\\\nSK g|g|8|g|c|40|0.064\\\\nSK i|j|h|k|c|41|0.064\\\\nEK l|0.064\\\\nEK l|0.064\\\\nM 9:\\\\"message\\\\"\\\\nM aa:\\\\"EXCEPT\\\\"\\\\nSK 9|g|aa|g|c|42|0.064\\\\nSK i|j|h|k|c|43|0.065\\\\nEK P|0.065\\\\nEK P|0.065\\\\nM ab:\\\\"FINALLY\\\\"\\\\nSK g|g|ab|g|c|44|0.065\\\\nSK i|j|h|k|c|45|0.065\\\\nEK l|0.065\\\\nEK l|0.065\\\\nET l|g|0.066\\\\nES T|0.067\\\\n"\')}}},n={};function t(o){var r=n[o];if(void 0!==r)return r.exports;var a=n[o]={id:o,exports:{}};return e[o](a,a.exports,t),a.exports}t.n=e=>{var n=e&&e.__esModule?()=>e.default:()=>e;return t.d(n,{a:n}),n},t.d=(e,n)=>{for(var o in n)t.o(n,o)&&!t.o(e,o)&&Object.defineProperty(e,o,{enumerable:!0,get:n[o]})},t.o=(e,n)=>Object.prototype.hasOwnProperty.call(e,n),t.nc=void 0,t(438),t(320)})();</script></body><script>window.setShowTime(true);\n    window.setShowExpand(true);\n    try {\n        const vscode = acquireVsCodeApi();\n        window.setVSCodeAPI(vscode);\n        document.getElementById("selectRunContainer").style.display = "block";\n    } catch (err) {\n        // That\'s ok (not running in VSCode).\n        window.setContents({\n            "initialContents": window.getSampleContents(),\n        });\n    }</script></html>'}

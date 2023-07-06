'use strict';

import { isDocumentDefined } from '../lib';

// Based on:
// https://stackoverflow.com/questions/37257911/detect-light-dark-theme-programatically-in-visual-studio-code

let found: 'vscode-light' | 'vscode-dark' | 'vscode-hc' | 'not-found' | undefined = undefined;

export function detectVSCodeTheme(): 'vscode-light' | 'vscode-dark' | 'vscode-hc' | 'not-found' {
  if (found !== undefined) {
    return found;
  }
  found = 'not-found';
  if (!isDocumentDefined()) {
    return found;
  }
  const body = document.body;

  if (body) {
    switch (body.className) {
      case 'vscode-light':
        found = 'vscode-light';
        break;
      case 'vscode-dark':
        found = 'vscode-dark';
        break;
      case 'vscode-high-contrast':
        found = 'vscode-hc';
        break;
    }
  }
  return found;
}

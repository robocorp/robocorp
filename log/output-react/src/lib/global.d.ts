import type { Entry } from './types';

declare global {
  interface Window {
    vscode: (entries: Entry[]) => void;
  }
}

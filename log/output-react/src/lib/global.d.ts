import type { Entry, EntryConsole } from './types';

declare global {
  interface Window {
    addEntries: (entries: Entry[]) => void;
    onChangedRun: (selectedRun: any) => void;
    setupScenario: (scenario: string) => void;
    setContents: (msg: ISetContentsRequest) => void;
    getSampleContents: (t) => any;

    setAllEntriesWhenPossible: (
      allEntries: Entry[],
      newExpanded: string[],
      updatedFromIndex: number,
    ) => void;
  }
}

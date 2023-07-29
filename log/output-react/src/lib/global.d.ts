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
      idToEntry: Map<string, Entry>,
      newExpanded: string[],
      updatedFromIndex: number,
    ) => void;
  }
}

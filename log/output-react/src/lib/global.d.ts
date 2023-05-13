import type { Entry } from './types';

declare global {
  interface Window {
    addEntries: (entries: Entry[]) => void;
    onChangedRun: (selectedRun: any) => void;
    setupScenario: (scenario: string) => void;
    setContents: (msg: ISetContentsRequest) => void;
    getSampleContents: (t) => any;

    setAllEntriesWhenPossible: (newEntries: Entry[], updatedFromIndex: number) => void;
  }
}

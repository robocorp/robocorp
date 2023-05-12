import type { Entry } from './types';

declare global {
  interface Window {
    addEntries: (entries: Entry[]) => void;
    setAllEntries: (newEntries: Entry[], updatedFromIndex: number) => void;
    onChangedRun: (selectedRun: any) => void;
    setContents: (msg: ISetContentsRequest) => void;
    getSampleContents: (t) => any;
  }
}

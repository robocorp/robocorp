import { Dispatch, SetStateAction, createContext, useContext } from 'react';

import { Run, RunTableEntry } from '~/lib/types';

export type ActionRunsContextType = {
  showRun: RunTableEntry | undefined;
  setShowRun: Dispatch<SetStateAction<Run | undefined>>;
};

export const ActionRunsContext = createContext<ActionRunsContextType>({
  showRun: undefined,
  setShowRun: () => {
    return null;
  },
});

export const useActionRunsContext = () => {
  return useContext(ActionRunsContext);
};

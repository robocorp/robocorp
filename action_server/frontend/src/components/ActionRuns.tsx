import { Badge, BadgeVariant, Box, Link, Panel, Table } from '@robocorp/components';
import {
  Dispatch,
  FC,
  MouseEvent,
  ReactNode,
  SetStateAction,
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';
import { useNavigate } from 'react-router-dom';
import { Action, Run, RunTableEntry } from '~/lib/types';
import { useActionServerContext } from '~/lib/actionServerContext';
import { refreshActions, refreshRuns } from '~/lib/requestData';
import { ActionRunDetails } from './ActionRunDetails';

export const NOT_RUN = 0;
export const RUNNING = 1;
export const PASSED = 2;
export const FAILED = 3;

export const StatusBadge: FC<{ rowData: Run }> = ({ rowData }) => {
  let variant: BadgeVariant = 'warning';
  let label: ReactNode = 'unset';

  if (rowData.status == NOT_RUN) {
    label = 'Not run';
    variant = 'primary';
  } else if (rowData.status == RUNNING) {
    label = 'Running';
    variant = 'info';
  } else if (rowData.status == PASSED) {
    label = 'Success';
    variant = 'success';
  } else if (rowData.status == FAILED) {
    label = 'Error';
    variant = 'danger';
  }

  return <Badge label={label} variant={variant}></Badge>;
};

const runRow: FC<{ rowData: RunTableEntry }> = ({ rowData }) => {
  const navigate = useNavigate();

  let result;
  if (rowData.status === PASSED) {
    result = rowData.result;
  } else if (rowData.status === FAILED) {
    result = rowData.error_message;
  }

  const { setShowRun } = useActionRunsContext();

  const onClickRun = useCallback(
    (event: MouseEvent) => {
      // navigate(`/runs/${rowData.id}`);
      setShowRun(rowData);
      event.stopPropagation();
    },
    [rowData],
  );

  return (
    <Table.Row>
      <Table.Cell>
        <Link onClick={onClickRun}>{rowData.action?.name}</Link>
      </Table.Cell>
      <Table.Cell>
        <StatusBadge rowData={rowData}></StatusBadge>
      </Table.Cell>
      <Table.Cell>{result}</Table.Cell>
    </Table.Row>
  );
};

export const ActionRuns: FC<{}> = () => {
  const columns = [
    {
      title: 'Name',
      id: 'name',
    },
    {
      title: 'State',
      id: 'state',
    },
    {
      title: 'Result',
      id: 'result',
    },
  ];

  const { loadedRuns, setLoadedRuns, loadedActions, setLoadedActions } = useActionServerContext();

  const [showRun, setShowRun] = useState<RunTableEntry | undefined>(undefined);

  useEffect(() => {
    refreshActions(loadedActions, setLoadedActions);
    refreshRuns(loadedRuns, setLoadedRuns);
  }, []);

  const isPending = loadedRuns.isPending || loadedActions.isPending;
  let runTableData: RunTableEntry[] = [];
  if (!isPending) {
    const loadedRunsData = loadedRuns.data || [];

    const actionIdToAction: Map<string, Action> = new Map();
    if (loadedRunsData.length > 0) {
      // Create dict of action id -> action name
      for (const actionPackage of loadedActions.data || []) {
        for (const action of actionPackage.actions) {
          actionIdToAction.set(action.id, action);
        }
      }

      for (const run of loadedRunsData) {
        const action = actionIdToAction.get(run.action_id);
        runTableData.push({ ...run, action: action });
      }
    }
  }

  const ctx: ActionRunsContextType = {
    showRun,
    setShowRun,
  };

  const contextMemoized = useMemo(() => ctx, [showRun, setShowRun]);

  if (loadedRuns.isPending || loadedActions.isPending) {
    return <Panel header={'Runs'} loading={true} empty={true} divider={true}></Panel>;
  }
  if (loadedRuns.errorMessage || loadedActions.errorMessage) {
    return (
      <Panel header={'Runs'} loading={false} empty={false} divider={true}>
        <Box p={20}>{`It was not possible to load the data. `}</Box>
        <Box p={20}>{`Error: ${loadedActions.errorMessage || loadedRuns.errorMessage}`}</Box>
      </Panel>
    );
  }

  return (
    <>
      <ActionRunsContext.Provider value={contextMemoized}>
        <Panel
          header={'Runs'}
          loading={isPending}
          empty={runTableData.length === 0}
          divider={false}
        >
          <Table columns={columns} data={runTableData} row={runRow} rowCount={10} />
        </Panel>
        <ActionRunDetails />
      </ActionRunsContext.Provider>
    </>
  );
};

export type ActionRunsContextType = {
  showRun: RunTableEntry | undefined;
  setShowRun: Dispatch<SetStateAction<RunTableEntry | undefined>>;
};

const ActionRunsContext = createContext<ActionRunsContextType>({
  showRun: undefined,
  setShowRun: () => {
    return null;
  },
});

export const useActionRunsContext = () => {
  return useContext(ActionRunsContext);
};

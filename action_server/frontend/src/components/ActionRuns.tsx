import { Badge, BadgeVariant, Box, Link, Panel, Table } from '@robocorp/components';
import { FC, ReactNode, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Run, RunTableEntry } from '~/lib/types';
import { useActionServerContext } from '~/lib/actionServerContext';
import { refreshActions, refreshRuns } from '~/lib/requestData';

const NOT_RUN = 0;
const RUNNING = 1;
const PASSED = 2;
const FAILED = 3;

const StatusBadge: FC<{ rowData: Run }> = ({ rowData }) => {
  let variant: BadgeVariant = 'warning';
  let label: ReactNode = 'unset';

  if (rowData.status == NOT_RUN) {
    label = 'Not run';
    variant = 'primary';
  } else if (rowData.status == RUNNING) {
    label = 'Running';
    variant = 'info';
  } else if (rowData.status == PASSED) {
    label = 'Passed';
    variant = 'success';
  } else if (rowData.status == FAILED) {
    label = 'Failed';
    variant = 'danger';
  }

  return <Badge label={label} variant={variant}></Badge>;
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

  const runRow: FC<{ rowData: RunTableEntry }> = ({ rowData }) => {
    const navigate = useNavigate();

    let result;
    if (rowData.status === PASSED) {
      result = rowData.result;
    } else if (rowData.status === FAILED) {
      result = rowData.error_message;
    }

    return (
      <Table.Row>
        <Table.Cell>
          <Link
            onClick={() => {
              navigate(`/runs/${rowData.id}`);
            }}
          >
            {rowData.action_name}
          </Link>
        </Table.Cell>
        <Table.Cell>
          <StatusBadge rowData={rowData}></StatusBadge>
        </Table.Cell>
        <Table.Cell>{result}</Table.Cell>
      </Table.Row>
    );
  };

  const { loadedRuns, setLoadedRuns, loadedActions, setLoadedActions } = useActionServerContext();
  useEffect(() => {
    refreshActions(loadedActions, setLoadedActions);
    refreshRuns(loadedRuns, setLoadedRuns);
  }, []);

  if (loadedRuns.errorMessage) {
    return (
      <Panel header={'Runs'} loading={true} empty={true} divider={false}>
        <Box
          p={20}
        >{`It was not possible to load the data. Error: ${loadedRuns.errorMessage}`}</Box>
      </Panel>
    );
  }

  const isPending = loadedRuns.isPending || loadedActions.isPending;
  let runTableData: RunTableEntry[] = [];
  if (!isPending) {
    const loadedRunsData = loadedRuns.data || [];

    const actionIdToName: Map<string, string> = new Map();
    if (loadedRunsData.length > 0) {
      // Create dict of action id -> action name
      for (const actionPackage of loadedActions.data || []) {
        for (const action of actionPackage.actions) {
          actionIdToName.set(action.id, action.name);
        }
      }

      for (const run of loadedRunsData) {
        const actionName = actionIdToName.get(run.action_id) || '<unable to get>';
        runTableData.push({ ...run, action_name: actionName });
      }
    }

  }
  return (
    <Panel header={'Runs'} loading={isPending} empty={runTableData.length === 0} divider={false}>
      <Table columns={columns} data={runTableData} row={runRow} rowCount={10} />
    </Panel>
  );
};

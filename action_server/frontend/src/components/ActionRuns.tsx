import { Badge, BadgeVariant, Box, Link, Panel, Table } from '@robocorp/components';
import { FC, ReactNode, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Run } from '~/lib/types';
import { useActionServerContext } from '~/lib/actionServerContext';
import { refreshRuns } from '~/lib/requestData';

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

  const runRow: FC<{ rowData: Run }> = ({ rowData }) => {
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
            {rowData.id}
          </Link>
        </Table.Cell>
        <Table.Cell>
          <StatusBadge rowData={rowData}></StatusBadge>
        </Table.Cell>
        <Table.Cell>{result}</Table.Cell>
      </Table.Row>
    );
  };

  const { loadedRuns, setLoadedRuns } = useActionServerContext();
  useEffect(() => {
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

  const isPending = loadedRuns.isPending;
  let data: Run[];
  if (isPending) {
    data = [];
  } else {
    data = loadedRuns.data || [];
  }
  return (
    <Panel header={'Runs'} loading={isPending} empty={data.length === 0} divider={false}>
      <Table columns={columns} data={data} row={runRow} rowCount={10} />
    </Panel>
  );
};

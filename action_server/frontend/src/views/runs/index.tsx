import { FC, MouseEvent, useCallback, useMemo, useState } from 'react';
import { useLocation, useNavigate, useSearchParams } from 'react-router-dom';
import {
  Button,
  Column,
  Filter,
  FilterGroup,
  Header,
  Input,
  SortDirection,
  Table,
  TableRowProps,
  Tooltip,
} from '@robocorp/components';
import { IconExpand } from '@robocorp/icons';
import { IconFileText, IconSearch } from '@robocorp/icons/iconic';

import { RunStatus, RunTableEntry } from '~/lib/types';
import { useActionServerContext } from '~/lib/actionServerContext';
import { Duration, Timestamp, StatusBadge, ViewLoader, ViewError } from '~/components';
import { baseUrl } from '~/lib/requestData';

import { ActionRunsContext, useActionRunsContext } from './components/context';
import { ActionRunDetails } from './components/ActionRunDetails';

const RunRow: FC<TableRowProps<RunTableEntry>> = ({ rowData: run }) => {
  const { setShowRun } = useActionRunsContext();
  const navigate = useNavigate();

  const onClickRun = useCallback(
    (event: MouseEvent) => {
      setShowRun(run);
      event.stopPropagation();
    },
    [run],
  );

  const onClickAction = useCallback(
    (event: MouseEvent) => {
      navigate(`/actions/${run.action_id}`);
      event.stopPropagation();
    },
    [run],
  );

  return (
    <Table.Row onClick={onClickRun}>
      <Table.Cell>#{run.numbered_id}</Table.Cell>
      <Table.Cell>
        <Button onClick={onClickAction} variant="ghost" size="small" iconAfter={IconExpand}>
          {run.action?.name}
        </Button>
      </Table.Cell>
      <Table.Cell>
        <StatusBadge status={run.status} />
      </Table.Cell>
      <Table.Cell>
        <Timestamp timestamp={run.start_time} />
      </Table.Cell>
      <Table.Cell>
        <Duration seconds={run.run_time} />
      </Table.Cell>
      <Table.Cell controls>
        <Tooltip text="View log">
          <Button
            icon={IconFileText}
            aria-label="Log"
            variant="ghost"
            forwardedAs="a"
            href={`${baseUrl}/api/runs/${run.id}/log.html`}
            target="_blank"
          />
        </Tooltip>
      </Table.Cell>
    </Table.Row>
  );
};

const columns: Column[] = [
  {
    title: 'Run',
    id: 'id',
    width: 50,
    sortable: true,
  },
  {
    title: 'Action',
    id: 'action',
    sortable: true,
  },
  {
    title: 'Status',
    id: 'status',
    sortable: true,
  },
  {
    title: 'Start Time',
    id: 'start_time',
    sortable: true,
  },
  {
    title: 'Run Time',
    id: 'run_time',
    sortable: true,
  },
  {
    title: '',
    id: 'actions',
    width: 50,
  },
];

export const ActionRuns: FC = () => {
  const [searchParams] = useSearchParams();
  const [sort, onSort] = useState<[string, SortDirection] | null>(['start_time', 'desc']);
  const [search, setSearch] = useState<string>(searchParams.get('search') || '');
  const { loadedRuns, loadedActions } = useActionServerContext();
  const [showRun, setShowRun] = useState<RunTableEntry | undefined>(undefined);
  const [selectedStates, setSelectedStates] = useState({ Status: [] as string[] });

  const contextMemoized = useMemo(
    () => ({
      showRun,
      setShowRun,
    }),
    [showRun, setShowRun],
  );

  const stateOptions = {
    Status: {
      label: 'Status',
      permanent: true,
      options: [
        { label: 'Failed', value: `${RunStatus.FAILED}`, itemType: 'checkbox' },
        { label: 'Not Run', value: `${RunStatus.NOT_RUN}`, itemType: 'checkbox' },
        { label: 'Successful', value: `${RunStatus.PASSED}`, itemType: 'checkbox' },
        { label: 'Running', value: `${RunStatus.RUNNING}`, itemType: 'checkbox' },
      ],
    } satisfies FilterGroup,
  };

  const data = useMemo(() => {
    const actions = loadedActions.data?.flatMap((item) => item.actions) || [];

    const runs =
      loadedRuns.data
        ?.map(
          (run) =>
            ({
              ...run,
              action: actions.find((action) => action.id === run.action_id),
            }) satisfies RunTableEntry,
        )
        .filter(
          (row) =>
            (selectedStates.Status.length === 0 ||
              selectedStates.Status.includes(row.status.toString())) &&
            row.action?.name.toLowerCase().includes(search.toLocaleLowerCase()),
        ) || [];

    const [id, direction] = sort ?? [];

    runs.sort((a, b) => {
      const aItem = a[id as keyof typeof a];
      const bItem = b[id as keyof typeof b];

      if (!aItem || !bItem) {
        return 0;
      }
      if (aItem < bItem) {
        return direction === 'asc' ? -1 : 1;
      }
      if (aItem > bItem) {
        return direction === 'asc' ? 1 : -1;
      }
      return 0;
    });

    return runs;
  }, [loadedRuns.data, loadedActions.data, sort, selectedStates, search]);

  if (loadedRuns.isPending) {
    return <ViewLoader />;
  }

  if (
    loadedRuns.errorMessage ||
    loadedActions.errorMessage ||
    loadedActions.isPending ||
    !loadedRuns.data
  ) {
    return (
      <ViewError>
        It was not possible to load the data.
        <br />
        {`Error: ${loadedActions.errorMessage}`}
      </ViewError>
    );
  }

  return (
    <ActionRunsContext.Provider value={contextMemoized}>
      <Header>
        <Header.Title title="Action Runs" />
      </Header>
      <Filter
        contentBefore={
          <Input
            iconLeft={IconSearch}
            placeholder="Search..."
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            aria-label="Search"
          />
        }
        options={stateOptions}
        values={selectedStates}
        onChange={setSelectedStates}
      />
      <Table sort={sort} onSort={onSort} columns={columns} data={data} row={RunRow} rowCount={10} />
      <ActionRunDetails />
    </ActionRunsContext.Provider>
  );
};

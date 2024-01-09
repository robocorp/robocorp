import { FC, MouseEvent, useCallback, useMemo, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  Box,
  Button,
  Column,
  EmptyState,
  Filter,
  FilterGroup,
  Header,
  Input,
  Link,
  SortDirection,
  Table,
  TableRowProps,
  Tooltip,
} from '@robocorp/components';
import { IconExpand } from '@robocorp/icons';
import {
  IconArrowUpRight,
  IconFileText,
  IconInformation,
  IconSearch,
} from '@robocorp/icons/iconic';

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
    width: 150,
    sortable: true,
  },
  {
    title: 'Start Time',
    id: 'start_time',
    sortable: true,
    width: 200,
  },
  {
    title: 'Run Time',
    id: 'run_time',
    sortable: true,
    width: 200,
  },
  {
    title: '',
    id: 'actions',
    width: 50,
  },
];

export const ActionRuns: FC = () => {
  const navigate = useNavigate();
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

  const stateOptions = useMemo(
    () => ({
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
    }),
    [],
  );

  const runs = useMemo(() => {
    const actions = loadedActions.data?.flatMap((item) => item.actions) || [];

    const filteredRuns =
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

    filteredRuns.sort((a, b) => {
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

    return filteredRuns;
  }, [loadedRuns.data, loadedActions.data, sort, selectedStates, search]);

  const onNavigateActions = useCallback(() => {
    navigate('/actions');
  }, []);

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

  if (!loadedRuns.data.length) {
    return (
      <Box
        display="flex"
        flex="1"
        justifyContent="center"
        flexDirection="column"
        minHeight="100%"
        pb="$64"
      >
        <EmptyState
          title="No action runs"
          description="Once actions are run, the output will appear here."
          action={<Button onClick={onNavigateActions}>Go to actions</Button>}
          secondaryAction={
            <Link
              icon={IconInformation}
              iconAfter={IconArrowUpRight}
              href="https://github.com/robocorp/robocorp"
              target="_blank"
              rel="noopener"
              variant="subtle"
              fontWeight="medium"
            >
              Learn more
            </Link>
          }
        />
      </Box>
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
      <Table sort={sort} onSort={onSort} columns={columns} data={runs} row={RunRow} rowCount={20} />
      <ActionRunDetails />
    </ActionRunsContext.Provider>
  );
};

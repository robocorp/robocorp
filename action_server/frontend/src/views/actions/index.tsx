import { FC, useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Badge, Column, Header, Table, TableRowProps } from '@robocorp/components';
import { IconExpand } from '@robocorp/icons';

import { useActionServerContext } from '~/lib/actionServerContext';
import { Action, ActionPackage, Run } from '~/lib/types';
import { ViewError, ViewLoader } from '~/components';

import { ActionDetails } from './components/ActionDetails';
import { Welcome } from '../welcome';

const ActionRow: FC<TableRowProps<Action, { packages: ActionPackage[]; runs: Run[] }>> = ({
  rowData: action,
  props: { packages, runs },
}) => {
  const navigate = useNavigate();

  const actionPackage = useMemo(
    () => packages.find((item) => item.id === action.action_package_id),
    [action],
  );

  const runCount = useMemo(
    () => runs?.filter((item) => item.action_id === action.id).length || 0,
    [action, runs],
  );

  const onClickAction = useCallback(() => {
    navigate(`/actions/${action.id}`);
  }, [action]);

  const onOpenRuns = useCallback(() => {
    navigate(`/runs?search=${action.name}`);
  }, [action]);

  return (
    <Table.Row onClick={onClickAction}>
      <Table.Cell>{action.name}</Table.Cell>
      <Table.Cell>
        {action.file}:{action.lineno}
      </Table.Cell>
      <Table.Cell>{actionPackage?.name}</Table.Cell>
      <Table.Cell controls>
        <Badge
          onClick={onOpenRuns}
          forwardedAs="button"
          variant="primary"
          iconAfter={IconExpand}
          label={runCount}
        />
      </Table.Cell>
    </Table.Row>
  );
};

const columns: Column[] = [
  { id: 'name', title: 'Action' },
  { id: 'location', title: 'Location' },
  { id: 'package', title: 'Package' },
  { id: 'runs', title: 'Runs' },
];

export const ActionPackages = () => {
  const { loadedActions, loadedRuns } = useActionServerContext();

  const actions = useMemo(() => {
    return loadedActions.data?.flatMap((item) => item.actions) || [];
  }, [loadedActions.data]);

  const tableProps = useMemo(() => {
    return {
      packages: loadedActions.data || [],
      runs: loadedRuns.data || [],
    };
  }, [loadedActions, loadedRuns]);

  if (loadedActions.isPending) {
    return <ViewLoader />;
  }

  if (loadedActions.errorMessage || !loadedActions.data) {
    return (
      <ViewError>
        It was not possible to load the data.
        <br />
        {`Error: ${loadedActions.errorMessage}`}
      </ViewError>
    );
  }

  if (actions.length === 0) {
    return <Welcome />;
  }

  return (
    <>
      <Header>
        <Header.Title title="Action Packages" />
      </Header>
      <Table
        columns={columns}
        data={actions}
        row={ActionRow}
        rowProps={tableProps}
        rowCount="all"
      />
      <ActionDetails />
    </>
  );
};

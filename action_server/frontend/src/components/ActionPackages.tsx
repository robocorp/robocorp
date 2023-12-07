import { Box, Button, Grid, Header, Link, Panel } from '@robocorp/components';
import {
  Dispatch,
  FC,
  MouseEvent,
  SetStateAction,
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
} from 'react';
import { useActionServerContext } from '~/lib/actionServerContext';
import { Action, ActionPackage } from '~/lib/types';
import { ActionDetails } from './ActionDetails';
import { IconPlay } from '@robocorp/icons';

const ActionComponent: FC<{ action: Action; actionPackage: ActionPackage }> = ({
  action,
  actionPackage,
}) => {
  const { setShowAction } = useActionsContext();

  const onClickAction = useCallback(
    (event: MouseEvent) => {
      // navigate(`/runs/${rowData.id}`);
      setShowAction({ action, actionPackage, showRunControls: false });
      event.stopPropagation();
    },
    [action],
  );

  const onClickActionShowRunControls = useCallback(
    (event: MouseEvent) => {
      // navigate(`/runs/${rowData.id}`);
      setShowAction({ action, actionPackage, showRunControls: true });
      event.stopPropagation();
    },
    [action],
  );

  return (
    <Box p={20} key={action.id} style={{ marginLeft: 25 }}>
      <Grid columns={2} gap={10}>
        <Link onClick={onClickAction}>{action.name}</Link>
        <Button variant="secondary" onClick={onClickActionShowRunControls}>
          <IconPlay size={'small'} />
        </Button>
      </Grid>
    </Box>
  );
};

export const ActionPackages = () => {
  const { loadedActions, setLoadedActions } = useActionServerContext();
  const [showAction, setShowAction] = useState<ShowActionInfo | undefined>(undefined);

  const isPending = loadedActions.isPending;
  let data: ActionPackage[];
  if (isPending) {
    data = [];
  } else {
    data = loadedActions.data || [];
  }

  const contents = [];
  for (const actionPackage of data) {
    const children = [];
    for (const action of actionPackage.actions) {
      children.push(
        <ActionComponent key={action.id} action={action} actionPackage={actionPackage} />,
      );
    }
    const header = <strong>{actionPackage.name}</strong>;
    contents.push(
      <Panel key={actionPackage.id} header={header}>
        {children}
      </Panel>,
    );
  }

  const ctx: ActionsContextType = {
    showAction,
    setShowAction,
  };

  const contextMemoized = useMemo(() => ctx, [showAction, setShowAction]);

  if (loadedActions.isPending) {
    return <Panel header={'Actions'} loading={true} empty={true} divider={true}></Panel>;
  }
  if (loadedActions.errorMessage) {
    return (
      <Panel header={'Actions'} loading={false} empty={false} divider={true}>
        <Box p={20}>{`It was not possible to load the data. `}</Box>
        <Box p={20}>{`Error: ${loadedActions.errorMessage}`}</Box>
      </Panel>
    );
  }

  return (
    <div>
      <ActionsContext.Provider value={contextMemoized}>
        <Header>
          <Header.Title title="Action Packages"></Header.Title>
        </Header>
        {contents}
        <ActionDetails />
      </ActionsContext.Provider>
    </div>
  );
};

interface ShowActionInfo {
  action: Action;
  actionPackage: ActionPackage;
  showRunControls: boolean;
}

export type ActionsContextType = {
  showAction: ShowActionInfo | undefined;
  setShowAction: Dispatch<SetStateAction<ShowActionInfo | undefined>>;
};

const ActionsContext = createContext<ActionsContextType>({
  showAction: undefined,
  setShowAction: () => {
    return null;
  },
});

export const useActionsContext = () => {
  return useContext(ActionsContext);
};

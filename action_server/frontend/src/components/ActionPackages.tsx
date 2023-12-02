import { Badge, Box, Header, Link, Panel } from '@robocorp/components';
import {
  Dispatch,
  FC,
  MouseEvent,
  SetStateAction,
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';
import { useActionServerContext } from '~/lib/actionServerContext';
import { refreshActions } from '~/lib/requestData';
import { Action, ActionPackage } from '~/lib/types';
import { ActionDetails } from './ActionDetails';

const ActionComponent: FC<{ action: Action }> = ({ action }) => {
  const { setShowAction } = useActionsContext();

  const onClickAction = useCallback(
    (event: MouseEvent) => {
      // navigate(`/runs/${rowData.id}`);
      setShowAction(action);
      event.stopPropagation();
    },
    [action],
  );
  return (
    <Box p={20} key={action.id} style={{ marginLeft: 25 }}>
      <Link onClick={onClickAction}>{action.name}</Link>
    </Box>
  );
};

export const ActionPackages = () => {
  const { loadedActions, setLoadedActions } = useActionServerContext();
  const [showAction, setShowAction] = useState<Action | undefined>(undefined);

  useEffect(() => {
    refreshActions(loadedActions, setLoadedActions);
  }, []);

  if (loadedActions.errorMessage) {
    return (
      <Panel header={'Actions'} loading={true} empty={true} divider={false}>
        <Box
          p={20}
        >{`It was not possible to load the data. Error: ${loadedActions.errorMessage}`}</Box>
      </Panel>
    );
  }

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
      children.push(<ActionComponent key={action.id} action={action} />);
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

export type ActionsContextType = {
  showAction: Action | undefined;
  setShowAction: Dispatch<SetStateAction<Action | undefined>>;
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

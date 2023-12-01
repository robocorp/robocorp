import { Badge, Box, Header, Panel } from '@robocorp/components';
import { useEffect } from 'react';
import { useActionServerContext } from '~/lib/actionServerContext';
import { refreshActions } from '~/lib/requestData';
import { ActionPackage } from '~/lib/types';

export const ActionPackages = () => {
  const { loadedActions, setLoadedActions } = useActionServerContext();
  
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
      children.push(
        <Box p={20} key={action.id} style={{marginLeft:25}}>
          {action.name}
        </Box>,
      );
    }
    const header = <strong>{actionPackage.name}</strong>;
    contents.push(
      <Panel key={actionPackage.id} header={header}>
        {children}
      </Panel>,
    );
  }

  return (
    <div>
      <Header>
        <Header.Title title="Action Packages">
        </Header.Title>
      </Header>
      {contents}
    </div>
  );
};

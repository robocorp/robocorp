import { FC, useCallback, useMemo } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Badge, Drawer, Tabs, Tooltip } from '@robocorp/components';

import { useActionServerContext } from '~/lib/actionServerContext';
import { ActionRun } from './ActionRun';
import { ActionDocumentation } from './ActionDocs';

export const ActionDetails: FC = () => {
  const navigate = useNavigate();
  const { actionId } = useParams();
  const { loadedActions } = useActionServerContext();

  const { action, actionPackage } = useMemo(() => {
    const packageExists = loadedActions.data?.find((item) =>
      item.actions.some((curr) => curr.id === actionId),
    );

    const actionExists = packageExists?.actions.find((item) => item.id === actionId);

    return {
      action: actionExists,
      actionPackage: packageExists,
    };
  }, [actionId]);

  const onClose = useCallback(() => {
    navigate('/actions');
  }, []);

  return (
    <Drawer onClose={onClose} width={760} open={!!action}>
      {action && actionPackage && (
        <>
          <Drawer.Header>
            <Drawer.Header.Title title={action.name} />
            <Drawer.Header.Badges>
              {!action.enabled && (
                <Tooltip text="This action has been removed or renamed and is not available for running">
                  <Badge variant="warning" size="small" label="Not available" />
                </Tooltip>
              )}
            </Drawer.Header.Badges>
          </Drawer.Header>
          <Drawer.Content>
            <Tabs>
              {action.enabled && <Tabs.Tab>Run</Tabs.Tab>}
              <Tabs.Tab>Documentation</Tabs.Tab>
              {action.enabled && (
                <Tabs.Panel>
                  <ActionRun action={action} actionPackage={actionPackage} />
                </Tabs.Panel>
              )}
              <Tabs.Panel>
                <ActionDocumentation action={action} />
              </Tabs.Panel>
            </Tabs>
          </Drawer.Content>
        </>
      )}
    </Drawer>
  );
};

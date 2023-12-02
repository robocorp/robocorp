import { FC, useCallback } from 'react';
import { Counter } from '~/lib/helpers';
import { prettyPrint } from '~/lib/prettyPrint';
import { Action } from '~/lib/types';
import { MarginBotton, Variable } from './Common';
import { useActionsContext } from './ActionPackages';
import { Drawer } from '@robocorp/components';

export const ActionRawDetails: FC<{ action: Action | undefined }> = ({ action }) => {
  const counter = new Counter();
  const contents = [];

  let inputSchema = action?.input_schema;
  if (!inputSchema) {
    inputSchema = '<unable to get input schema>';
  }

  let outputSchema = action?.output_schema;
  if (!outputSchema) {
    outputSchema = '<unable to get output schema>';
  }

  let docs = action?.docs;
  if (docs === undefined) {
    docs = '';
  }

  contents.push(<Variable key={counter.next()} name={`Documentation`} value={docs} />);

  contents.push(
    <Variable key={counter.next()} name={`Input Schema`} value={prettyPrint(inputSchema)} />,
  );

  contents.push(
    <Variable key={counter.next()} name={`Output Schema`} value={prettyPrint(outputSchema)} />,
  );

  return <>{contents}</>;
};

export const ActionDetails: FC<{}> = ({}) => {
  const { showAction, setShowAction } = useActionsContext();
  const onClose = useCallback(() => {
    setShowAction(undefined);
  }, []);

  if (showAction === undefined) {
    return <></>;
  }

  return (
    <Drawer passive onClose={onClose} width={1024} open={true}>
      <Drawer.Header>
        <Drawer.Header.Title title={showAction.name} />
      </Drawer.Header>
      <Drawer.Content>
        <ActionRawDetails action={showAction} />
        <MarginBotton />
      </Drawer.Content>
    </Drawer>
  );
};

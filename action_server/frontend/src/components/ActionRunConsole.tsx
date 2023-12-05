import { FC, useState } from 'react';
import { useLoaderData } from 'react-router-dom';
import { collectRunArtifacts } from '~/lib/requestData';
import { LoadedArtifacts } from '~/lib/types';
import { PreBox } from './Common';
import { Box } from '@robocorp/components';

export async function actionRunConsoleLoader(args: any) {
  const params = args.params;
  return { id: params.id };
}

export const ActionRunConsole: FC<{}> = () => {
  const data = useLoaderData() as any;
  const runId = data.id;

  const [loadedArtifacts, setLoadedActions] = useState<LoadedArtifacts>({
    isPending: true,
    requestedOnce: false,
    data: [],
    errorMessage: undefined,
  });

  if (!loadedArtifacts.requestedOnce) {
    collectRunArtifacts(runId, loadedArtifacts, setLoadedActions, {artifact_names: ['__action_server_output.txt']});
  }

  let output = loadedArtifacts?.data['__action_server_output.txt'];
  if (output === undefined) {
    output = '<unable to get output>';
  }

  return (
    <Box style={{ marginLeft: 10 }}>
      <PreBox>{output}</PreBox>
    </Box>
  );
};

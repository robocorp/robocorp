import { FC, useEffect, useState } from 'react';
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

  const [loadedArtifacts, setLoadedArtifacts] = useState<LoadedArtifacts>({
    isPending: true,
    data: [],
    errorMessage: undefined,
  });

  useEffect(() => {
    // console.log('collect artifacts mounted');
    collectRunArtifacts(runId, setLoadedArtifacts, {
      artifact_names: ['__action_server_output.txt'],
    });

    return () => {
      // console.log('collect artifacts UNMOUNTED');
    };
  }, []);

  let output = '<unexpected state getting output>';
  if (loadedArtifacts.isPending) {
    output = 'Please wait, the console content is being fetched...';
  } else if (loadedArtifacts.errorMessage) {
    output = loadedArtifacts.errorMessage;
  } else {
    const data = loadedArtifacts?.data;
    if (data === undefined) {
      output = '<unable to get output>';
    } else {
      output = loadedArtifacts?.data['__action_server_output.txt'];
      if (output === undefined) {
        output = '<unable to get output>';
      }
    }
  }

  return (
    <Box style={{ marginLeft: 10 }}>
      <PreBox>{output}</PreBox>
    </Box>
  );
};

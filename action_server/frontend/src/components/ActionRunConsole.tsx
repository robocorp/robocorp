import { FC, useEffect, useState } from 'react';
import { collectRunArtifacts } from '~/lib/requestData';
import { LoadedArtifacts } from '~/lib/types';
import { Progress } from '@robocorp/components';
import { Code } from '~/components';

type Props = {
  runId: string;
};

export const ActionRunConsole: FC<Props> = ({ runId }) => {
  const [loadedArtifacts, setLoadedArtifacts] = useState<LoadedArtifacts>({
    isPending: true,
    data: {},
    errorMessage: undefined,
  });

  useEffect(() => {
    collectRunArtifacts(runId, setLoadedArtifacts, {
      artifact_names: ['__action_server_output.txt'],
    });
  }, []);

  if (loadedArtifacts.isPending) {
    return <Progress />;
  }

  let output = '<unexpected state getting output>';

  if (loadedArtifacts.errorMessage) {
    output = loadedArtifacts.errorMessage;
  } else {
    const data = loadedArtifacts?.data;
    if (data === undefined) {
      output = '<unable to get output>';
    } else {
      output = data['__action_server_output.txt'] || '<unable to get output>';
    }
  }

  return <Code value={output} />;
};

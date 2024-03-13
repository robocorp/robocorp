import { FC } from 'react';
import { Header } from '@robocorp/components';

import { ActionRunConsole, Code } from '~/components';

type Props = {
  result: string;
  runId: string;
};

export const ActionRunResult: FC<Props> = ({ result, runId }) => {
  return (
    <>
      <Header size="small">
        <Header.Title title="Result" />
      </Header>
      <Code lineNumbers={false} value={result} />

      <Header size="small">
        <Header.Title title="Console output" />
      </Header>
      <ActionRunConsole runId={runId} />
    </>
  );
};

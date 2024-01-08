import { FC } from 'react';
import { Header } from '@robocorp/components';

import { Code } from '~/components';
import { prettyPrint } from '~/lib/helpers';
import { Action } from '~/lib/types';

type Props = {
  action: Action;
};

export const ActionDocumentation: FC<Props> = ({ action }) => {
  return (
    <>
      <Header size="small">
        <Header.Title title="Documentation" />
      </Header>
      <Code value={action.docs || ''} />

      <Header size="small">
        <Header.Title title="Input Schema" />
      </Header>
      <Code value={prettyPrint(action.input_schema)} lang="json" />

      <Header size="small">
        <Header.Title title="Output Schema" />
      </Header>
      <Code value={prettyPrint(action.output_schema)} lang="json" />
    </>
  );
};

import { Box, Header } from '@robocorp/components';
import { FC } from 'react';
import styled from 'styled-components';

import { Entry, EntryVariable } from '~/lib/types';
import { Bold, FormatHeaderActions, LocationContent, SourceAndLine, VariableValue } from './Common';

const Content = styled(Box)`
  position: relative;
`;

export const VariableComponent: FC<{ entry: Entry }> = (props) => {
  const entryVariable: EntryVariable = props.entry as EntryVariable;

  return (
    <Content>
      <Header size="medium">
        <Header.Title title="Variable Value" />
        <FormatHeaderActions />
      </Header>
      <VariableValue value={entryVariable.value}></VariableValue>
      <SourceAndLine source={entryVariable.source} lineno={entryVariable.lineno}></SourceAndLine>
    </Content>
  );
};

import { Box, Header } from '@robocorp/components';
import { FC } from 'react';
import styled from 'styled-components';

import { Entry, EntryTask } from '~/lib/types';
import { SourceAndLine } from './Common';

const Content = styled(Box)`
  position: relative;
`;

export const TaskComponent: FC<{ entry: Entry }> = (props) => {
  const entryTask: EntryTask = props.entry as EntryTask;

  return (
    <Content>
      <SourceAndLine source={entryTask.source} lineno={entryTask.lineno}></SourceAndLine>
    </Content>
  );
};

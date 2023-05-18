import { Box, Header } from '@robocorp/components';
import { FC } from 'react';
import styled from 'styled-components';

import { Entry, EntryTask } from '~/lib/types';
import { Bold, LocationContent } from './Common';

const Content = styled(Box)`
  position: relative;
`;

export const TaskComponent: FC<{ entry: Entry }> = (props) => {
  const entryTask: EntryTask = props.entry as EntryTask;

  return (
    <Content>
      <Header size="medium">
        <Header.Title title="Location" />
      </Header>
      <LocationContent>
        <Bold>File:</Bold> {entryTask.source}
      </LocationContent>
      <LocationContent>
        <Bold>Line:</Bold> {entryTask.lineno}
      </LocationContent>
    </Content>
  );
};

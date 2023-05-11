import { Box } from '@robocorp/components';

import { useLogContext } from '~/lib';
import { Body, Header } from './components';

export const Table = () => {
  const { viewSettings } = useLogContext();

  return (
    <Box role="table" aria-label="Log entries">
      <Header role="row">
        <Header.Column flex="1">Step</Header.Column>
        {viewSettings.columns.location && <Header.Column flex="0 0 6rem">Location</Header.Column>}
        {viewSettings.columns.duration && <Header.Column flex="0 0 6rem">Duration</Header.Column>}
      </Header>
      <Body role="rowgroup" />
    </Box>
  );
};

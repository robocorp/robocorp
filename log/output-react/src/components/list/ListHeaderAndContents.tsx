import { Box } from '@robocorp/components';

import { useLogContext } from '~/lib';
import { ListHeader } from './components/ListHeader';
import { ListContents } from './components/ListContents';

export const ListHeaderAndContents = () => {
  const { viewSettings } = useLogContext();

  return (
    <Box role="table" aria-label="Log entries">
      <ListHeader role="row">
        <ListHeader.Column flex="1">Step</ListHeader.Column>
        {viewSettings.columns.location && (
          <ListHeader.Column flex="0 0 6rem">Location</ListHeader.Column>
        )}
        {viewSettings.columns.duration && (
          <ListHeader.Column flex="0 0 6rem">Duration</ListHeader.Column>
        )}
      </ListHeader>
      <ListContents role="rowgroup" />
    </Box>
  );
};

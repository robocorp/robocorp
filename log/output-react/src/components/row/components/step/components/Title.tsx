import { FC, ReactNode } from 'react';
import { Box, Typography } from '@robocorp/components';

import { Entry, EntryMethod, EntryTask, EntryException, Type } from '~/lib/types';

type Props = {
  entry: Entry;
};

const getTitle = (entry: Entry): ReactNode => {
  switch (entry.type) {
    case Type.task:
      return (entry as EntryTask).name;
    case Type.method:
      return (entry as EntryMethod).name;
    case Type.exception:
      return ''; // the type is added in the icon.
    // return (entry as EntryException).excType;
    default:
      return 'TODO: provide getTitle';
  }
};

export const Title: FC<Props> = ({ entry }) => {
  return (
    <Box minWidth={0} className="entryName">
      <Typography mr="$24" lineHeight="$32" variant="body.small" fontWeight="medium" truncate={1}>
        {getTitle(entry)}
      </Typography>
    </Box>
  );
};

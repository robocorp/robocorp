import { FC, ReactNode } from 'react';
import { Box, Typography } from '@robocorp/components';

import { Entry, Type } from '~/lib/types';

type Props = {
  entry: Entry;
};

const getTitle = (entry: Entry): ReactNode => {
  switch (entry.type) {
    case Type.task:
    // fallthrough
    case Type.suite:
      return entry.name;
    case Type.variable:
      return `Variable: ${entry.name}`;
    case Type.log:
      return entry.message;
    default:
      return '';
  }
};

export const Title: FC<Props> = ({ entry }) => {
  return (
    <Box minWidth={0}>
      <Typography mr="$24" lineHeight="$32" variant="body.small" fontWeight="medium" truncate={1}>
        {getTitle(entry)}
      </Typography>
    </Box>
  );
};

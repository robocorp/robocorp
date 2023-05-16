import { FC, ReactNode } from 'react';
import { Box, Typography } from '@robocorp/components';
import { styled } from '@robocorp/theme';

import { Entry, Type } from '~/lib/types';

type Props = {
  entry: Entry;
};

const Container = styled(Box)`
  flex: 1;
  min-width: 0px;
  height: auto;

  > pre {
    max-height: ${({ theme }) => theme.space.$48};
  }
`;

const getValue = (entry: Entry): ReactNode => {
  switch (entry.type) {
    case Type.variable:
      return entry.value;
    default:
      return 'TODO: provide getValue for: ' + entry.type;
  }
};

export const Value: FC<Props> = ({ entry }) => {
  return (
    <Container flex="1">
      <Typography
        mr="$8"
        mt={6}
        as="pre"
        fontFamily="code"
        variant="body.small"
        color="content.subtle.light"
        fontWeight="bold"
        truncate={1}
      >
        {getValue(entry)}
      </Typography>
    </Container>
  );
};

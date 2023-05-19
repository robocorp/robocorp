import { FC, ReactNode } from 'react';
import { Box, Typography } from '@robocorp/components';
import { styled } from '@robocorp/theme';

import {
  Entry,
  EntryException,
  EntryGenerator,
  EntryMethodBase,
  EntrySuspendYield,
  EntryUntrackedGenerator,
  EntryVariable,
  Type,
} from '~/lib/types';
import { formatArguments } from '~/lib/helpers';

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
    case Type.method:
    case Type.generator:
    case Type.untrackedGenerator:
    case Type.resumeYield:
    case Type.resumeYieldFrom:
      return formatArguments(entry as EntryMethodBase | EntryGenerator | EntryUntrackedGenerator);
    case Type.task:
      return '';
    case Type.suspendYieldFrom:
      return '';
    case Type.exception:
      return (entry as EntryException).excMsg;
    case Type.variable:
      const entryVariable = entry as EntryVariable;
      return `${entryVariable.value} (${entryVariable.varType})`;
    case Type.suspendYield:
      const entrySuspendYield = entry as EntrySuspendYield;
      return `Yielded: ${entrySuspendYield.value} (${entrySuspendYield.varType})`;
    default:
      return 'TODO: provide getValue for: ' + entry.type;
  }
};

export const Value: FC<Props> = ({ entry }) => {
  return (
    <Container flex="1" className="entryValue">
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

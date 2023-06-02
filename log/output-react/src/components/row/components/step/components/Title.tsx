import { FC, ReactNode } from 'react';
import { Box, Typography } from '@robocorp/components';

import {
  Entry,
  EntryMethod,
  EntryTask,
  EntryException,
  Type,
  EntryVariable,
  EntryGenerator,
  EntryUntrackedGenerator,
  EntryResumeYield,
  EntryResumeYieldFrom,
  EntrySuspendYield,
  EntrySuspendYieldFrom,
  EntryThreadDump,
} from '~/lib/types';

type Props = {
  entry: Entry;
};

export const getTitle = (entry: Entry): string => {
  switch (entry.type) {
    case Type.task:
      return (entry as EntryTask).name;
    case Type.processSnapshot:
      return '';
    case Type.threadDump:
      return `Thread Stack: ${(entry as EntryThreadDump).threadName}`;
    case Type.generator:
      return `${(entry as EntryGenerator).name} (enter generator)`;
    case Type.untrackedGenerator:
      return `${(entry as EntryUntrackedGenerator).name} (generator lifecycle untracked)`;
    case Type.resumeYield:
      return `${(entry as EntryResumeYield).name} (resume generator)`;
    case Type.resumeYieldFrom:
      return `${(entry as EntryResumeYieldFrom).name} (resume generator)`;
    case Type.suspendYield:
      return `${(entry as EntrySuspendYield).name} (suspend generator)`;
    case Type.suspendYieldFrom:
      return `${(entry as EntrySuspendYieldFrom).name} (suspend generator)`;
    case Type.method:
      return (entry as EntryMethod).name;
    case Type.log:
      return ''; // the log type is added in the icon.
    case Type.variable:
      return (entry as EntryVariable).name;
    case Type.exception:
      return ''; // the type is added in the icon.
    // return (entry as EntryException).excType;
    default:
      return 'TODO: provide getTitle';
  }
};

export const Title: FC<Props> = ({ entry }) => {
  const title = getTitle(entry);
  if (!title) {
    return <></>;
  }

  return (
    <Box minWidth={0} className="entryName">
      <Typography mr="$24" lineHeight="$32" variant="body.small" fontWeight="medium" truncate={1}>
        {title}
      </Typography>
    </Box>
  );
};

import { FC, MouseEvent, useCallback } from 'react';
import { Box, Typography } from '@robocorp/components';

import {
  Entry,
  EntryMethod,
  EntryTask,
  Type,
  EntryVariable,
  EntryGenerator,
  EntryUntrackedGenerator,
  EntryResumeYield,
  EntryResumeYieldFrom,
  EntrySuspendYield,
  EntrySuspendYieldFrom,
  EntryThreadDump,
  EntryIf,
  EntryElse,
  EntryAssertFailed,
} from '~/lib/types';
import { useLogContext } from '~/lib';

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
    case Type.assertFailed:
      return (entry as EntryAssertFailed).name;
    case Type.ifElement:
      return `Entered "${(entry as EntryIf).name}"`;
    case Type.elseElement:
      return `Entered "${(entry as EntryElse).name}"`;
    case Type.returnElement:
      return `Return`;
    case Type.log:
      return ''; // the log type is added in the icon.
    case Type.console:
      return ''; // Not much to add...
    case Type.variable:
      return (entry as EntryVariable).name;
    case Type.exception:
      return ''; // the type is added in the icon.
    // return (entry as EntryException).excType;
    default:
      console.log('TODO: Provide getTitle for', entry);
      return 'TODO: provide getTitle';
  }
};

export const StepTitle: FC<Props> = ({ entry }) => {
  const title = getTitle(entry);
  if (!title) {
    return <></>;
  }

  const { setDetailsIndex } = useLogContext();

  const onClickShowDetails = useCallback(
    (e: MouseEvent) => {
      e.stopPropagation();
      setDetailsIndex({ indexAll: entry.entryIndexAll });
    },
    [entry],
  );

  return (
    <Box
      minWidth={0}
      className="entryName"
      onClick={onClickShowDetails}
      style={{ cursor: 'pointer' }}
    >
      <Typography mr="$24" lineHeight="$32" variant="body.small" fontWeight="medium" truncate={1}>
        {title}
      </Typography>
    </Box>
  );
};

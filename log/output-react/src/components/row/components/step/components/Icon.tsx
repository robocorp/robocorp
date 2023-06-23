import { FC, ReactNode } from 'react';
import { IconBox, IconCircle, IconInformation, IconWarningTriangle } from '@robocorp/icons/iconic';
import {
  IconAtSign,
  IconCpu,
  IconEmptyCircle,
  IconFrame,
  IconLogOut,
  IconPauseCircle,
  IconPlayCircle,
  IconQuestionCircle,
  IconStatusCompleted,
  IconStatusError,
  IconStatusIdle,
  IconTable,
} from '@robocorp/icons';
import { Badge, Box } from '@robocorp/components';

import {
  Entry,
  EntryException,
  EntryLog,
  EntryMethodBase,
  EntryResumeYield,
  EntryResumeYieldFrom,
  EntryTask,
  StatusLevel,
  Type,
} from '~/lib/types';
import { Color } from '@robocorp/theme/types';

type Props = {
  entry: Entry;
};

const getLogIcon = (status: StatusLevel): ReactNode => {
  switch (status) {
    case StatusLevel.error:
      return <IconStatusError color="background.error" />;
    case StatusLevel.warn:
      return <IconWarningTriangle color="background.notification" />;
    case StatusLevel.info:
      return <IconStatusIdle color="background.accent" />;
    case StatusLevel.success:
      return <IconStatusCompleted color="background.success" />;
    case StatusLevel.unset:
      return <IconEmptyCircle color="background.notification" />;
    default:
      return <IconInformation color="blue60" />;
  }
};
function getColorFromStatus(status: StatusLevel): Color {
  let useColor: Color = 'background.success';
  switch (status) {
    case StatusLevel.error:
      useColor = 'background.error';
      break;
    case StatusLevel.warn:
      useColor = 'background.notification';
      break;
    case StatusLevel.info:
      useColor = 'background.accent';
      break;
    case StatusLevel.unset:
      useColor = 'background.success';
  }
  return useColor;
}

const getTaskIcon = (status: StatusLevel): ReactNode => {
  return <IconAtSign color={getColorFromStatus(status)} size="small" />;
};

const getGeneratorIcon = (status: StatusLevel): ReactNode => {
  return <IconPlayCircle color={getColorFromStatus(status)} size="small" />;
};

const getUntrackedGeneratorIcon = (): ReactNode => {
  // Note that we don't have a status for an untracked generator.
  return <IconFrame color="background.success" size="small" />;
};

const getResumeYieldIcon = (status: StatusLevel): ReactNode => {
  // Note that we don't have a status for an untracked generator.
  return <IconPlayCircle color={getColorFromStatus(status)} size="small" />;
};

const getSuspendYieldIcon = (): ReactNode => {
  return <IconPauseCircle color="magenta60" size="small" />;
};

export const getIcon = (entry: Entry): ReactNode => {
  switch (entry.type) {
    case Type.task:
      const entryTask: EntryTask = entry as EntryTask;
      return getTaskIcon(entryTask.status);
    case Type.method:
      return getLogIcon((entry as EntryMethodBase).status);
    case Type.ifElement:
      return <IconQuestionCircle color="magenta60" size="small" />;
    case Type.elseElement:
      return <IconCircle color="magenta60" size="medium" />;
    case Type.returnElement:
      return <IconLogOut color="magenta60" size="small" />;
    case Type.generator:
      return getGeneratorIcon((entry as EntryMethodBase).status);
    case Type.untrackedGenerator:
      return getUntrackedGeneratorIcon();
    case Type.resumeYield:
    case Type.resumeYieldFrom:
      return getResumeYieldIcon((entry as EntryResumeYield | EntryResumeYieldFrom).status);
    case Type.suspendYield:
    case Type.suspendYieldFrom:
      return getSuspendYieldIcon();
    case Type.variable:
      return <IconBox color="blue60" size="small" />;
    case Type.log:
      const log: EntryLog = entry as EntryLog;
      switch (log.status) {
        case StatusLevel.error:
          return (
            <Badge
              icon={IconStatusError}
              variant="danger"
              iconColor="background.error"
              label={'ERROR'}
              size="small"
            />
          );
        case StatusLevel.warn:
          return (
            <Badge
              icon={IconWarningTriangle}
              variant="warning"
              label={'WARN'}
              size="small"
              iconColor="background.notification"
            />
          );
        default:
          return (
            <Badge
              icon={IconInformation}
              label={'INFO'}
              size="small"
              iconColor="blue60"
              variant="info"
            />
          );
      }
    case Type.exception:
      const exc: EntryException = entry as EntryException;
      return (
        <Badge
          icon={IconStatusError}
          variant="danger"
          iconColor="background.error"
          label={exc.excType}
          size="small"
        />
      );
    case Type.processSnapshot:
      return (
        <Badge
          icon={IconCpu}
          label={'Process Snapshot'}
          iconColor="blue60"
          variant="blue"
          size="small"
        />
      );
    case Type.threadDump:
      return <IconTable size="small" color="blue60" />;
    // return (
    //   <Badge
    //     icon={IconTable}
    //     label={'Thread Stack'}
    //     iconColor="blue60"
    //     variant="blue"
    //     size="small"
    //   />
    // );
    default:
      return <IconInformation color="blue60" />;
  }
};

export const Icon: FC<Props> = ({ entry }) => {
  return (
    <Box display="flex" alignItems="center" height="$32" mr="$8">
      {getIcon(entry)}
    </Box>
  );
};

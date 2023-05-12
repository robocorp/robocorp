import { FC, ReactNode } from 'react';
import {
  IconBox,
  IconCloseCircle,
  IconInformation,
  IconWarningTriangle,
} from '@robocorp/icons/iconic';
import {
  IconEmptyCircle,
  IconStatusCompleted,
  IconStatusError,
  IconStatusIdle,
} from '@robocorp/icons';
import { Badge, Box } from '@robocorp/components';

import { Entry, StatusLevel, Type } from '~/lib/types';

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

const getIcon = (entry: Entry): ReactNode => {
  switch (entry.type) {
    case Type.suite:
      return <IconCloseCircle color="red60" />;
    case Type.variable:
      return <IconBox color="magenta60" />;
    case Type.log:
      return getLogIcon(entry.status);
    case Type.task:
      return getLogIcon(entry.status);
    case Type.error:
      return (
        <Badge
          icon={IconStatusError}
          variant="danger"
          iconColor="background.error"
          label="Execution Error"
          size="small"
        />
      );
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

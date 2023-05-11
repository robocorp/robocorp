import { FC, ReactNode } from 'react';
import {
  IconBox,
  IconCloseCircle,
  IconInformation,
  IconWarningTriangle,
} from '@robocorp/icons/iconic';
import { IconStatusError } from '@robocorp/icons';
import { Badge, Box } from '@robocorp/components';

import { Entry, Status, Type } from '~/lib/types';

type Props = {
  entry: Entry;
};

const getLogIcon = (status: Status): ReactNode => {
  switch (status) {
    case Status.warn:
      return <IconWarningTriangle color="background.notification" />;
    case Status.info:
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

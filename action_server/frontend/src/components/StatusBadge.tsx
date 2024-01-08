import { FC, useMemo } from 'react';
import { Badge } from '@robocorp/components';

import { RunStatus } from '~/lib/types';

type Props = {
  status: RunStatus;
  size?: 'small' | 'medium';
};

export const StatusBadge: FC<Props> = ({ status, size }) => {
  const { label, variant } = useMemo(() => {
    switch (status) {
      case RunStatus.RUNNING:
        return {
          label: 'Running',
          variant: 'info' as const,
        };
      case RunStatus.PASSED:
        return {
          label: 'Success',
          variant: 'success' as const,
        };
      case RunStatus.FAILED:
        return {
          label: 'Failed',
          variant: 'danger' as const,
        };
      case RunStatus.NOT_RUN:
      default:
        return {
          label: 'Not run',
          variant: 'primary' as const,
        };
    }
  }, [status]);

  return <Badge size={size} label={label} variant={variant} />;
};

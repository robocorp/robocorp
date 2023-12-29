import { FC } from 'react';

type Props = {
  timestamp?: string;
  showMilliSeconds?: boolean;
};

export const Timestamp: FC<Props> = (props: Props) => {
  const { timestamp, showMilliSeconds } = props;

  if (timestamp) {
    const dateVar = new Date(timestamp);
    const stringVar = dateVar.toLocaleString('sv-SE');
    return showMilliSeconds
      ? `${stringVar}.${String(dateVar.getMilliseconds()).padStart(3, '0')}`
      : stringVar;
  }

  return null;
};

Timestamp.defaultProps = {
  timestamp: undefined,
  showMilliSeconds: false,
};

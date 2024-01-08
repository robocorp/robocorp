import { FC } from 'react';
import { format, addSeconds, addMinutes } from 'date-fns';

interface Props {
  seconds?: number | null;
}

const DURATION_MINUTE = 60;
const DURATION_HOUR = DURATION_MINUTE * 60;
const DURATION_DAY = DURATION_HOUR * 24;

const getFormatter = (seconds: number) => {
  if (seconds < DURATION_MINUTE) return "s's'";
  if (seconds < DURATION_HOUR) return "m'm 'ss's'";
  if (seconds < DURATION_DAY) return "h'h 'mm'm 'ss's'";
  return null;
};

export const Duration: FC<Props> = ({ seconds = 0 }) => {
  if (typeof seconds !== 'number') return <>0</>;

  const formatter = getFormatter(seconds);

  if (!formatter) {
    const days = Math.floor(seconds / DURATION_DAY);
    const reminder = seconds % DURATION_DAY;
    const reminderFormatter = getFormatter(reminder);
    if (!reminderFormatter) return <>{seconds}s</>;
    const dt = addSeconds(new Date(0), reminder);
    return `${days}d ${format(addMinutes(dt, dt.getTimezoneOffset()), reminderFormatter)}`;
  }

  const dt = addSeconds(new Date(0), seconds);
  return <>{format(addMinutes(dt, dt.getTimezoneOffset()), formatter)}</>;
};

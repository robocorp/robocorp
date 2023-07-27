import { Drawer, Box } from '@robocorp/components';
import { formatTimeInSeconds, useLogContext } from '~/lib';
import { PreBox } from './components/Common';
import { useCallback } from 'react';

export const InformationDetails = () => {
  const { runInfo, setDetailsIndex } = useLogContext();
  const onClose = useCallback(() => {
    setDetailsIndex(null);
  }, []);

  const msgs: string[] = [];

  const time: string = runInfo.time;
  const timeDelta: number | undefined = runInfo.finishTimeDeltaInSeconds;
  let timeDescription = '';
  if (time && time.length > 0) {
    timeDescription = time;
    msgs.push('Start time: ' + timeDescription);

    if (timeDelta !== undefined) {
      msgs.push('Time to run: ' + formatTimeInSeconds(timeDelta));
    }
  }

  for (const msg of runInfo.infoMessages) {
    msgs.push(msg);
  }
  return (
    <Drawer passive onClose={onClose} width={1024} open={true}>
      <Drawer.Header>
        <Drawer.Header.Title title={'General Information'} />
      </Drawer.Header>
      <Box p="$16" margin="$8">
        <PreBox>{msgs.join('\n')}</PreBox>
      </Box>
    </Drawer>
  );
};

import { Box, Drawer } from '@robocorp/components';
import { useCallback } from 'react';

import { useLogContext } from '~/lib';
import { Content, Title } from './components';
import { PreBox } from './components/content/components/Common';

export const Details = () => {
  const { filteredEntries, activeIndex, setActiveIndex, runInfo } = useLogContext();
  const onClose = useCallback(() => {
    setActiveIndex(null);
  }, []);

  if (activeIndex == 'information') {
    const msgs: string[] = [];
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
  } else {
    const entry = typeof activeIndex === 'number' && filteredEntries.entries[activeIndex];

    return (
      <Drawer passive onClose={onClose} width={1024} open={!!entry}>
        {entry && (
          <>
            <Title entry={entry} />
            <Content entry={entry} />
          </>
        )}
      </Drawer>
    );
  }
};

import { Drawer } from '@robocorp/components';
import { useCallback } from 'react';

import { useLogContext } from '~/lib';
import { Content, Title } from './components';

export const Details = () => {
  const { filteredEntries, activeIndex, setActiveIndex } = useLogContext();
  const entry = typeof activeIndex === 'number' && filteredEntries.entries[activeIndex];

  const onClose = useCallback(() => {
    setActiveIndex(null);
  }, []);

  return (
    <Drawer passive onClose={onClose} open={!!entry}>
      {entry && (
        <>
          <Title entry={entry} />
          <Content entry={entry} />
        </>
      )}
    </Drawer>
  );
};

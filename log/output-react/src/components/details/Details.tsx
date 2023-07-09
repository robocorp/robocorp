import { Box, Drawer } from '@robocorp/components';
import { useCallback } from 'react';
import { useLogContext } from '~/lib';
import { styled } from '@robocorp/theme';
import { DetailsTitle } from './DetailsTitle';
import { DetailsContent } from './DetailsContent';
import { InformationDetails } from './InformationDetails';
import { TerminalDetails } from './TerminalDetails';

export const BoxOutput = styled(Box)`
  display: inline;
  font-family: consolas, inconsolata, monaco, menlo, Droid Sans Mono, monospace;
`;

export const Details = () => {
  const { filteredEntries, activeIndex, setActiveIndex } = useLogContext();

  if (activeIndex == 'information') {
    return <InformationDetails></InformationDetails>;
  } else if (activeIndex == 'terminal') {
    return <TerminalDetails></TerminalDetails>;
  } else {
    const entry = typeof activeIndex === 'number' && filteredEntries.entries[activeIndex];
    const onClose = useCallback(() => {
      setActiveIndex(null);
    }, []);

    return (
      <Drawer passive onClose={onClose} width={1024} open={!!entry}>
        {entry && (
          <>
            <DetailsTitle entry={entry} />
            <DetailsContent entry={entry} />
          </>
        )}
      </Drawer>
    );
  }
};

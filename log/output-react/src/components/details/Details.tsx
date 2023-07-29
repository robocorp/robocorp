import { Box, Drawer } from '@robocorp/components';
import { useCallback } from 'react';
import { DetailsIndexSelected, useLogContext } from '~/lib';
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
  const { detailsIndex, setDetailsIndex, entriesInfo } = useLogContext();
  const onClose = useCallback(() => {
    setDetailsIndex(null);
  }, []);

  if (!detailsIndex) {
    return <></>;
  }

  if (detailsIndex == 'information') {
    return <InformationDetails></InformationDetails>;
  } else if (detailsIndex == 'terminal') {
    return <TerminalDetails></TerminalDetails>;
  } else {
    const idx = detailsIndex as DetailsIndexSelected;
    const entry = entriesInfo.allEntries[idx.indexAll];

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

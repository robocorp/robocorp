import { Box, Drawer } from '@robocorp/components';
import { useCallback } from 'react';

import { Counter, useLogContext } from '~/lib';
import { Content, Title } from './components';
import { PreBox } from './components/content/components/Common';
import { ConsoleMessageKind, EntryConsole, Type } from '~/lib/types';
import { styled } from '@robocorp/theme';

export const BoxOutput = styled(Box)`
  display: inline;
  font-family: consolas, inconsolata, monaco, menlo, Droid Sans Mono, monospace;
`;

export const Details = () => {
  const { filteredEntries, activeIndex, setActiveIndex, runInfo, consoleEntries, viewSettings } =
    useLogContext();
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
  } else if (activeIndex == 'terminal') {
    let msgs: any[] = [];
    let buf: string[] = [];
    const counter = new Counter();

    const addBufferContents = (entry: EntryConsole) => {
      if (buf.length > 0) {
        switch (entry.kind) {
          case ConsoleMessageKind.stderr:
          case ConsoleMessageKind.error:
          case ConsoleMessageKind.traceback:
            msgs.push(
              <BoxOutput color="background.error" key={counter.next()}>
                {buf.join('')}
              </BoxOutput>,
            );
            break;

          case ConsoleMessageKind.regular:
          case ConsoleMessageKind.task_name:
          case ConsoleMessageKind.important:
            const color: 'blue50' | 'blue90' = viewSettings.theme === 'dark' ? 'blue50' : 'blue90';
            msgs.push(
              <BoxOutput color={color} key={counter.next()}>
                {buf.join('')}
              </BoxOutput>,
            );
            break;
          // case ConsoleMessageKind.unset:
          // case ConsoleMessageKind.processSnapshot:
          // case ConsoleMessageKind.stdout:
          default:
            msgs.push(<BoxOutput key={counter.next()}>{buf.join('')}</BoxOutput>);
        }
        buf = [];
      }
    };

    const addNewLine = (entry: EntryConsole) => {
      addBufferContents(entry);
      msgs.push(<br key={counter.next()} />);
    };

    for (let entry of consoleEntries) {
      if (entry.type == Type.console) {
        const c = entry as EntryConsole;

        let i: number = 0;
        let skipNextNewLine = false;

        for (let char of c.message) {
          i += 1;
          if (char === '\n') {
            if (skipNextNewLine) {
              skipNextNewLine = false;
              continue;
            }
            addNewLine(c);
            continue;
          }
          if (char === '\r') {
            skipNextNewLine = true;
            addNewLine(c);
            continue;
          }
          buf.push(char);
        }
        addBufferContents(c);
      }
    }
    return (
      <Drawer passive onClose={onClose} width={1024} open={true}>
        <Drawer.Header>
          <Drawer.Header.Title title={'Terminal Output'} />
        </Drawer.Header>
        <Box p="$16" margin="$8">
          {msgs}
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

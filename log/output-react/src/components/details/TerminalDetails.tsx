import { Drawer, Box, Button, Menu } from '@robocorp/components';
import { Counter, useLogContext } from '~/lib';
import {
  EntryConsole,
  ConsoleMessageKind,
  Type,
  StatusLevel,
  EntryLog,
  ViewSettings,
} from '~/lib/types';
import { BoxOutput } from './Details';
import { IconChevronDown } from '@robocorp/icons';
import { CustomActions } from '~/lib/CustomActions';
import { useCallback } from 'react';

type TerminalColors = 'background.error' | 'blue50' | 'blue90' | 'purple70' | 'purple50';

const getConsoleColor = (
  entry: EntryConsole,
  viewSettings: ViewSettings,
): undefined | TerminalColors => {
  switch (entry.kind) {
    case ConsoleMessageKind.stderr:
    case ConsoleMessageKind.error:
    case ConsoleMessageKind.traceback:
      return 'background.error';

    case ConsoleMessageKind.regular:
    case ConsoleMessageKind.task_name:
    case ConsoleMessageKind.important:
      const color: 'blue50' | 'blue90' = viewSettings.theme === 'dark' ? 'blue50' : 'blue90';
      return color;
    // case ConsoleMessageKind.unset:
    // case ConsoleMessageKind.processSnapshot:
    // case ConsoleMessageKind.stdout:
    default:
      return undefined;
  }
};

const getLogColor = (entry: EntryLog, viewSettings: ViewSettings): undefined | TerminalColors => {
  switch (entry.status) {
    case StatusLevel.error:
    case StatusLevel.warn:
      return 'background.error';

    default:
      const color: 'purple50' | 'purple70' =
        viewSettings.theme === 'dark' ? 'purple50' : 'purple70';
      return color;
  }
};

class AddMessages {
  buf: string[] = [];
  msgs: any[] = [];
  counter = new Counter();

  constructor() {}

  addNewLine(color: TerminalColors | undefined) {
    this.addBufferContents(color);
    this.msgs.push(<br key={this.counter.next()} />);
  }

  addBufferContents(color: TerminalColors | undefined) {
    if (this.buf.length > 0) {
      this.msgs.push(
        <BoxOutput color={color} key={this.counter.next()}>
          {this.buf.join('')}
        </BoxOutput>,
      );
    }
    this.buf.length = 0;
  }

  addMessage(color: TerminalColors | undefined, message: string) {
    let i: number = 0;
    let skipNextNewLine = false;
    for (let char of message) {
      i += 1;
      if (char === '\n') {
        if (skipNextNewLine) {
          skipNextNewLine = false;
          continue;
        }
        this.addNewLine(color);
        continue;
      }
      if (char === '\r') {
        skipNextNewLine = true;
        this.addNewLine(color);
        continue;
      }
      this.buf.push(char);
    }
    this.addBufferContents(color);
  }
}

export const TerminalDetails = () => {
  const { allEntries, viewSettings, setViewSettings, setActiveIndex } = useLogContext();
  const onClose = useCallback(() => {
    setActiveIndex(null);
  }, []);

  const addMessages = new AddMessages();

  const showInTerminal = viewSettings.showInTerminal;

  for (let entry of allEntries) {
    if (entry.type == Type.log) {
      const c = entry as EntryLog;
      if (!c.isHtml) {
        if ((c.status & showInTerminal) !== 0) {
          const color = getLogColor(c, viewSettings);
          addMessages.addMessage(color, c.message);
        }
      }
    } else if (entry.type == Type.console) {
      const c = entry as EntryConsole;
      const color = getConsoleColor(c, viewSettings);
      addMessages.addMessage(color, c.message);
    }
  }
  const onClickDebug = useCallback(() => {
    setViewSettings((curr) => ({
      ...curr,
      showInTerminal: curr.showInTerminal ^ StatusLevel.debug,
    }));
  }, []);
  const onClickInfo = useCallback(() => {
    setViewSettings((curr) => ({
      ...curr,
      showInTerminal: curr.showInTerminal ^ StatusLevel.info,
    }));
  }, []);
  const onClickWarn = useCallback(() => {
    setViewSettings((curr) => ({
      ...curr,
      showInTerminal: curr.showInTerminal ^ StatusLevel.warn,
    }));
  }, []);
  const onClickCritical = useCallback(() => {
    setViewSettings((curr) => ({
      ...curr,
      showInTerminal: curr.showInTerminal ^ StatusLevel.error,
    }));
  }, []);
  return (
    <Drawer passive onClose={onClose} width={1024} open={true}>
      <Drawer.Header>
        <Drawer.Header.Title title={'Terminal Output'} />
      </Drawer.Header>
      <CustomActions>
        <Menu
          trigger={
            <Button icon={IconChevronDown} aria-label="Show log messages">
              {'Show log messages in output'}
            </Button>
          }
          leaveMenuOpenOnItemSelect
        >
          <Menu.Title>Show in Output</Menu.Title>
          <Menu.Checkbox
            checked={(viewSettings.showInTerminal & StatusLevel.debug) !== 0}
            onClick={onClickDebug}
          >
            {'Debug'}
          </Menu.Checkbox>
          <Menu.Checkbox
            checked={(viewSettings.showInTerminal & StatusLevel.info) !== 0}
            onClick={onClickInfo}
          >
            {'Info'}
          </Menu.Checkbox>
          <Menu.Checkbox
            checked={(viewSettings.showInTerminal & StatusLevel.warn) !== 0}
            onClick={onClickWarn}
          >
            {'Warn'}
          </Menu.Checkbox>
          <Menu.Checkbox
            checked={(viewSettings.showInTerminal & StatusLevel.error) !== 0}
            onClick={onClickCritical}
          >
            {'Critical'}
          </Menu.Checkbox>
        </Menu>
      </CustomActions>
      <Box p="$16" margin="$8">
        {addMessages.msgs}
      </Box>
    </Drawer>
  );
};

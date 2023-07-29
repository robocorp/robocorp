import { Drawer, Box, Button, Menu } from '@robocorp/components';
import { Counter, useLogContext } from '~/lib';
import '../details/components/Common.css';
import {
  EntryConsole,
  ConsoleMessageKind,
  Type,
  StatusLevel,
  EntryLog,
  ViewSettings,
  Entry,
} from '~/lib/types';
import { BoxOutput } from './Details';
import { IconChevronDown } from '@robocorp/icons';
import { CustomActions } from '~/lib/CustomActions';
import { FC, useCallback } from 'react';
import { isInVSCode } from '~/vscode/vscodeComm';
import { getOpts } from '~/treebuild/options';

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

const Message: FC<{
  entry: Entry;
  color: TerminalColors | undefined;
  text: string;
  counter: Counter;
}> = ({ entry, color, text, counter }) => {
  let data: any = undefined;
  if (entry.type === Type.log && isInVSCode()) {
    const c = entry as EntryLog;
    if (c.source && c.lineno) {
      data = {
        source: c.source,
        lineno: c.lineno,
      };
    }
  }

  const onClick = useCallback((entryId: any, data: any) => {
    if (data === undefined) {
      return;
    }
    const opts = getOpts();
    if (opts !== undefined && opts.onClickReference !== undefined) {
      opts.onClickReference(data);
    }
  }, []);

  return (
    <BoxOutput
      className={data !== undefined ? 'locationLink' : undefined}
      color={color}
      key={counter.next()}
      onClick={() => {
        onClick(entry.id, data);
      }}
    >
      {text}
    </BoxOutput>
  );
};

class Messages {
  buf: string[] = [];
  msgs: any[] = [];
  counter = new Counter();

  constructor() {}

  addNewLine(entry: Entry, color: TerminalColors | undefined) {
    this.addBufferContents(entry, color);
    this.msgs.push(<br key={this.counter.next()} />);
  }

  addBufferContents(entry: Entry, color: TerminalColors | undefined): boolean {
    if (this.buf.length > 0) {
      this.msgs.push(
        <Message
          entry={entry}
          color={color}
          text={this.buf.join('')}
          key={this.counter.next()}
          counter={this.counter}
        ></Message>,
      );
      this.buf.length = 0;
      return true;
    }
    return false;
  }

  addMessage(
    entry: Entry,
    color: TerminalColors | undefined,
    message: string,
    requireNewLine: boolean,
  ) {
    let i: number = 0;
    let skipNextNewLine = false;
    let lastNewLine = false;
    for (let char of message) {
      i += 1;
      if (char === '\n') {
        if (skipNextNewLine) {
          skipNextNewLine = false;
          continue;
        }
        this.addNewLine(entry, color);
        lastNewLine = true;
        continue;
      }
      if (char === '\r') {
        skipNextNewLine = true;
        this.addNewLine(entry, color);
        lastNewLine = true;
        continue;
      }
      this.buf.push(char);
    }
    if (this.addBufferContents(entry, color)) {
      lastNewLine = false;
    }
    if (requireNewLine && !lastNewLine) {
      this.addNewLine(entry, color);
    }
  }
}

export const TerminalDetails = () => {
  const { entriesInfo, viewSettings, setViewSettings, setDetailsIndex } = useLogContext();

  const onClose = useCallback(() => {
    setDetailsIndex(null);
  }, []);

  const messages = new Messages();

  const showInTerminal = viewSettings.showInTerminal;

  for (let entry of entriesInfo.allEntries) {
    if (entry.type == Type.log) {
      const c = entry as EntryLog;
      if (!c.isHtml) {
        if ((c.status & showInTerminal) !== 0) {
          const color = getLogColor(c, viewSettings);
          messages.addMessage(entry, color, c.message, true);
        }
      }
    } else if (entry.type == Type.console) {
      const c = entry as EntryConsole;
      const color = getConsoleColor(c, viewSettings);
      messages.addMessage(entry, color, c.message, false);
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
        {messages.msgs}
      </Box>
    </Drawer>
  );
};

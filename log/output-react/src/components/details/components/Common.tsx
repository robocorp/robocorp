import {
  Box,
  Button,
  Code,
  EditorView,
  Header,
  Menu,
  Tooltip,
  useClipboard,
} from '@robocorp/components';
import { styled } from '@robocorp/theme';
import { FC, useCallback, useEffect, useMemo, useRef } from 'react';

import { prettyPrint } from '~/lib/prettyPrint';
import { python } from '@codemirror/lang-python';
import { useLogContext } from '~/lib';
import { IconChevronDown, IconCopy } from '@robocorp/icons';
import { IconCheck2 } from '@robocorp/icons/iconic';
import { FormatType } from '~/lib/types';
import { CustomActions } from '../../../lib/CustomActions';
import { isInVSCode } from '~/vscode/vscodeComm';
import { getOpts } from '~/treebuild/options';

export const Bold = styled(Box)`
  font-weight: bold;
  display: inline;
`;

export const LocationContent = styled(Box)`
  margin-left: ${({ theme }) => theme.space.$12};
  margin-bottom: ${({ theme }) => theme.space.$8};
  font-family: consolas, inconsolata, monaco, menlo, Droid Sans Mono, monospace;
`;

export const PreBox = styled(Box)`
  white-space: pre-wrap;
  word-break: break-word;
  display: inline;
  font-family: consolas, inconsolata, monaco, menlo, Droid Sans Mono, monospace;
`;

export const VariableContent = styled(Box)`
  margin-top: ${({ theme }) => theme.space.$8};
`;

export const SourceAndLine: FC<{ source: string; lineno: number }> = (props) => {
  let data: any = undefined;
  if (isInVSCode()) {
    if (props.source && props.lineno) {
      data = {
        source: props.source,
        lineno: props.lineno,
      };
    }
  }

  const onClick = useCallback((data: any) => {
    if (data === undefined) {
      return;
    }
    const opts = getOpts();
    if (opts !== undefined && opts.onClickReference !== undefined) {
      opts.onClickReference(data);
    }
  }, []);

  return (
    <>
      {props.source && props.lineno ? (
        <>
          <Header size="medium">
            <Header.Title title="Location" />
          </Header>

          <LocationContent
            className={data !== undefined ? 'locationLink' : undefined}
            onClick={() => {
              onClick(data);
            }}
          >
            <Bold>File:</Bold> {props.source}
          </LocationContent>
          <LocationContent
            className={data !== undefined ? 'locationLink' : undefined}
            onClick={() => {
              onClick(data);
            }}
          >
            <Bold>Line:</Bold> {props.lineno}
          </LocationContent>
        </>
      ) : (
        <></>
      )}
    </>
  );
};

export const VariableValue: FC<{ value: string }> = (props) => {
  const extensions = useMemo(() => {
    return [python()];
  }, []);

  const { viewSettings } = useLogContext();
  let value: string;
  switch (viewSettings.format) {
    case 'auto':
      if (props.value.includes('\n')) {
        value = props.value;
      } else {
        value = prettyPrint(props.value);
      }
      break;
    case 'raw':
      value = props.value;
      break;
    case 'pretty':
      value = prettyPrint(props.value);
      break;
  }

  const { onCopyToClipboard, copiedToClipboard } = useClipboard();

  const toolbar = useMemo(() => {
    return (
      <Tooltip text="Copy to clipboard">
        <Button
          aria-label="Copy to clipboard"
          variant="ghost"
          className="copyVariableToClipboard"
          icon={copiedToClipboard ? IconCheck2 : IconCopy}
          onClick={onCopyToClipboard(value)}
          size="small"
        />
      </Tooltip>
    );
  }, [copiedToClipboard, value]);

  let showLineNumbers = props.value.includes('\n');

  return (
    <Box>
      <VariableContent className="variableContent">
        <Code
          value={value}
          extensions={extensions}
          aria-label="Code editor"
          lineNumbers={showLineNumbers}
          readOnly={true}
        />
      </VariableContent>
      {toolbar}
    </Box>
  );
};

const getFormatLabel = (format: FormatType): string => {
  switch (format) {
    case 'auto':
      return 'Auto';
    case 'raw':
      return 'Original';
    case 'pretty':
      return 'Pretty print';
  }
  return `<unexpected: ${format}`;
};

export const FormatHeaderActions: FC<{}> = (props) => {
  const { viewSettings, setViewSettings } = useLogContext();
  const format = viewSettings.format;

  const onClickAuto = useCallback(() => {
    setViewSettings((curr) => ({
      ...curr,
      format: 'auto',
    }));
  }, []);

  const onClickRaw = useCallback(() => {
    setViewSettings((curr) => ({
      ...curr,
      format: 'raw',
    }));
  }, []);

  const onClickFormat = useCallback(() => {
    setViewSettings((curr) => ({
      ...curr,
      format: 'pretty',
    }));
  }, []);

  // Auto mode will pretty-print contents if no new lines are found in the text, otherwise the original content will be shown.
  return (
    <CustomActions>
      <Menu
        trigger={
          <Button icon={IconChevronDown} aria-label="Change format">
            {'Format: ' + getFormatLabel(format)}
          </Button>
        }
        leaveMenuOpenOnItemSelect
      >
        <Menu.Title>Format</Menu.Title>
        <Menu.Checkbox checked={format === 'auto'} onClick={onClickAuto}>
          {getFormatLabel('auto')}
        </Menu.Checkbox>
        <Menu.Checkbox checked={format === 'raw'} onClick={onClickRaw}>
          {getFormatLabel('raw')}
        </Menu.Checkbox>
        <Menu.Checkbox checked={format === 'pretty'} onClick={onClickFormat}>
          {getFormatLabel('pretty')}
        </Menu.Checkbox>
      </Menu>
    </CustomActions>
  );
};

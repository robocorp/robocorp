import { Box } from '@robocorp/components';
import { FC, useCallback, useState } from 'react';
import { Counter } from '~/lib';

import styled from 'styled-components';

import { Entry, EntryException, EntryThreadDump } from '~/lib/types';
import { Bold, FormatHeaderActions, VariableValue } from './Common';
import { PythonTraceback } from '~/treebuild/protocols';
import { IconTextAlignJustified, IconTextAlignLeft } from '@robocorp/icons/iconic';
import { isInVSCode } from '~/vscode/vscodeComm';
import { getOpts } from '~/treebuild/options';

const LocationContent = styled(Box)`
  margin-bottom: ${({ theme }) => theme.space.$8};
  margin-top: ${({ theme }) => theme.space.$8};
  font-family: consolas, inconsolata, monaco, menlo, Droid Sans Mono, monospace;
`;

const LineContents = styled(Box)`
  margin-bottom: ${({ theme }) => theme.space.$8};
  margin-top: ${({ theme }) => theme.space.$8};
  font-weight: bold;
  font-family: consolas, inconsolata, monaco, menlo, Droid Sans Mono, monospace;
  display: inline-block;
`;

const LineVar = styled(Box)`
  margin-bottom: ${({ theme }) => theme.space.$8};
  font-family: consolas, inconsolata, monaco, menlo, Droid Sans Mono, monospace;
`;

const Title = styled(Box)`
  margin-bottom: ${({ theme }) => theme.space.$8};
  font-family: consolas, inconsolata, monaco, menlo, Droid Sans Mono, monospace;
`;

export const ThreadDumpComponent: FC<{ entry: Entry }> = (props) => {
  return tracebackComponent(
    (props.entry as EntryThreadDump).tb,
    'Thread stack (most recent call last):',
  );
};

export const ExceptionComponent: FC<{ entry: Entry }> = (props) => {
  return tracebackComponent(
    (props.entry as EntryException).tb,
    'Traceback (most recent call last):',
  );
};

function* reversed(arr: any[]) {
  let i = arr.length - 1;

  while (i >= 0) {
    yield arr[i];
    i -= 1;
  }
}

function* enumerate(it: any) {
  let i = 0;
  for (const x of it) {
    yield [i++, x];
  }
}

function tracebackComponent(tb: PythonTraceback, title: string) {
  const onClick = useCallback((data: any) => {
    if (data === undefined) {
      return;
    }
    const opts = getOpts();
    if (opts !== undefined && opts.onClickReference !== undefined) {
      opts.onClickReference(data);
    }
  }, []);

  const counter = new Counter();

  const contents = [];

  if (tb.stack === undefined || tb.stack.length === 0) {
    return <>No stack found</>;
  }

  contents.push(
    <div style={{ marginBottom: '2em' }} key={counter.next()}>
      <FormatHeaderActions />
      <Title key={counter.next()}>{title}</Title>
    </div>,
  );
  for (const [index, tbe] of enumerate(reversed(tb.stack))) {
    let data: any = undefined;
    if (isInVSCode()) {
      if (tbe.source && tbe.lineno) {
        data = {
          source: tbe.source,
          lineno: tbe.lineno,
        };
      }
    }

    const isLast = index == tb.stack.length - 1;
    const locationContent = (
      <LocationContent
        key={counter.next()}
        className={data !== undefined ? 'locationLink' : undefined}
        onClick={() => {
          onClick(data);
        }}
      >
        File "<Bold key={counter.next()}>{tbe.source}</Bold>", line{' '}
        <Bold key={counter.next()}>{tbe.lineno}</Bold>, in{' '}
        <Bold key={counter.next()}>{tbe.method}</Bold>
      </LocationContent>
    );
    const lineContent = <LineContents key={counter.next()}>{tbe.lineContent}</LineContents>;

    const variablesContent = [];
    for (const [varName, varTypeAndVal] of tbe.variables) {
      const [varType, varValue] = varTypeAndVal;
      variablesContent.push(
        <LineVar key={counter.next()} style={{ whiteSpace: 'normal' }}>
          <Bold>
            <Bold color="blue50">❖</Bold> {varName}
          </Bold>{' '}
          ({varType})
        </LineVar>,
        <VariableValue key={counter.next()} value={varValue}></VariableValue>,
      );
    }

    contents.push(
      <details key={counter.next()} open={isLast}>
        <summary key={counter.next()}>{lineContent}</summary>
        <div key={counter.next()}>
          {locationContent} {variablesContent}
        </div>
      </details>,
    );

    if (!isLast) {
      contents.push(
        <hr
          key={counter.next()}
          color="gray"
          style={{ height: '1px', width: '96%', marginLeft: '2%' }}
        ></hr>,
      );
    }
  }

  return <>{contents}</>;
}

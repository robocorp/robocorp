import { Box } from '@robocorp/components';
import { FC } from 'react';
import { Counter } from '~/lib';

import styled from 'styled-components';

import { Entry, EntryException, EntryThreadDump } from '~/lib/types';
import { Bold } from './Common';
import { PythonTraceback } from '~/treebuild/protocols';

const LocationContent = styled(Box)`
  margin-left: ${({ theme }) => theme.space.$12};
  margin-bottom: ${({ theme }) => theme.space.$8};
  margin-top: ${({ theme }) => theme.space.$8};
  font-family: consolas, inconsolata, monaco, menlo, Droid Sans Mono, monospace;
`;

const LineContents = styled(Box)`
  margin-left: ${({ theme }) => theme.space.$20};
  margin-bottom: ${({ theme }) => theme.space.$8};
  font-weight: bold;
  font-family: consolas, inconsolata, monaco, menlo, Droid Sans Mono, monospace;
`;

const LineVar = styled(Box)`
  margin-left: ${({ theme }) => theme.space.$32};
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

function tracebackComponent(tb: PythonTraceback, title: string) {
  const counter = new Counter();

  const contents = [];

  contents.push(<Box key={counter.next()}>{title}</Box>);
  for (const tbe of reversed(tb.stack)) {
    contents.push(
      <LocationContent key={counter.next()}>
        File "<Bold key={counter.next()}>{tbe.source}</Bold>", line{' '}
        <Bold key={counter.next()}>{tbe.lineno}</Bold>, in{' '}
        <Bold key={counter.next()}>{tbe.method}</Bold>
      </LocationContent>,
    );
    contents.push(<LineContents key={counter.next()}>{'⪢ ' + tbe.lineContent}</LineContents>);
    for (const [varName, varTypeAndVal] of tbe.variables) {
      const [varType, varValue] = varTypeAndVal;
      contents.push(
        <LineVar key={counter.next()}>
          <Bold>
            <Bold color="blue50">❖</Bold> {varName}
          </Bold>{' '}
          ({varType}) = {varValue}
        </LineVar>,
      );
    }
    contents.push(
      <hr
        key={counter.next()}
        color="gray"
        style={{ height: '1px', width: '96%', marginLeft: '2%' }}
      ></hr>,
    );
  }
  // Remove the last hr
  contents.splice(-1);

  return <>{contents}</>;
}

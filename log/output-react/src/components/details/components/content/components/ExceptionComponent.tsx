import { Box } from '@robocorp/components';
import { FC, useState } from 'react';
import { Counter } from '~/lib';

import styled from 'styled-components';

import { Entry, EntryException, EntryThreadDump } from '~/lib/types';
import { Bold } from './Common';
import { PythonTraceback } from '~/treebuild/protocols';
import { IconTextAlignJustified, IconTextAlignLeft } from '@robocorp/icons/iconic';

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
  const counter = new Counter();

  const contents = [];

  const [isWrapped, setIsWrapped] = useState(false);

  const toggleTextWrap = () => {
    setIsWrapped(!isWrapped);
  };

  if (tb.stack === undefined || tb.stack.length === 0) {
    return <>No stack found</>;
  }

  contents.push(
    <div style={{ marginBottom: '2em' }} key={counter.next()}>
      <Title style={{ float: 'left' }} key={counter.next()}>
        {title}
      </Title>
      <Box
        style={{ float: 'right', cursor: 'pointer' }}
        onClick={toggleTextWrap}
        title={isWrapped ? 'Click to unwrap text' : 'Click to wrap text'}
      >
        {isWrapped ? (
          <IconTextAlignLeft color="blue60" />
        ) : (
          <IconTextAlignJustified color="blue60" />
        )}
      </Box>
    </div>,
  );
  for (const [index, tbe] of enumerate(reversed(tb.stack))) {
    const isLast = index == tb.stack.length - 1;
    const locationContent = (
      <LocationContent key={counter.next()}>
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
        <LineVar key={counter.next()} style={{ whiteSpace: isWrapped ? 'normal' : 'nowrap' }}>
          <Bold>
            <Bold color="blue50">❖</Bold> {varName}
          </Bold>{' '}
          ({varType}) = {varValue}
        </LineVar>,
      );
    }

    contents.push(
      <details key={counter.next()} open={isLast}>
        <summary>{lineContent}</summary>
        <div>
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

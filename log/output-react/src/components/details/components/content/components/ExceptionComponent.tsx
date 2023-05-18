import { Box } from '@robocorp/components';
import { FC } from 'react';
import { Counter } from '~/lib';

import styled from 'styled-components';

import { Entry, EntryException } from '~/lib/types';

const LocationContent = styled(Box)`
  margin-left: ${({ theme }) => theme.space.$12};
  margin-bottom: ${({ theme }) => theme.space.$8};
  margin-top: ${({ theme }) => theme.space.$8};
`;

const LineContents = styled(Box)`
  margin-left: ${({ theme }) => theme.space.$20};
  margin-bottom: ${({ theme }) => theme.space.$8};
  font-weight: bold;
`;

const LineVar = styled(Box)`
  margin-left: ${({ theme }) => theme.space.$32};
  margin-bottom: ${({ theme }) => theme.space.$8};
`;

const Bold = styled(Box)`
  font-weight: bold;
  display: inline;
`;

export const ExceptionComponent: FC<{ entry: Entry }> = (props) => {
  const counter = new Counter();

  const entryException: EntryException = props.entry as EntryException;
  const tb = entryException.tb;
  const contents = [];

  contents.push(<Box key={counter.next()}>Traceback (most recent call last):</Box>);
  for (const tbe of tb.stack) {
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
};

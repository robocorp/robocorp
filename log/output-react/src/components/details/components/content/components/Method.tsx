import { Box, Header, Typography } from '@robocorp/components';
import { FC } from 'react';
import styled from 'styled-components';

import { Entry, EntryMethodBase, EntrySuspendYield, Type } from '~/lib/types';
import { Bold, LocationContent } from './Common';
import { Counter } from '~/lib';

const Content = styled(Box)`
  position: relative;
`;

const ArgumentContent = styled(Box)`
  position: relative;
  margin-bottom: ${({ theme }) => theme.space.$8};
  margin-left: ${({ theme }) => theme.space.$8};
`;

const ArgumentName = styled(Box)`
  font-weight: bolder;
  display: inline;
  margin-left: ${({ theme }) => theme.space.$8};
  font-family: consolas, inconsolata, monaco, menlo, Droid Sans Mono, monospace;
`;

const ArgumentType = styled(Box)`
  margin-left: ${({ theme }) => theme.space.$8};
  display: inline;
  font-family: consolas, inconsolata, monaco, menlo, Droid Sans Mono, monospace;
`;

const ArgumentValue = styled(Box)`
  margin-left: ${({ theme }) => theme.space.$12};
  font-family: consolas, inconsolata, monaco, menlo, Droid Sans Mono, monospace;
`;

export const Method: FC<{ entry: Entry }> = (props) => {
  const entryMethod: EntryMethodBase = props.entry as EntryMethodBase;
  const argumentsList = [];
  let argumentsHeader = <></>;

  let counter = new Counter();
  if (entryMethod.arguments && entryMethod.arguments.length > 0) {
    argumentsHeader = (
      <Header size="medium">
        <Header.Title title="Arguments" />
      </Header>
    );
    for (const arg of entryMethod.arguments) {
      argumentsList.push(
        <ArgumentContent key={counter.next()} className="argument">
          <ArgumentName className="argumentName">{`${arg.name}`}</ArgumentName>
          <ArgumentType>{`(type: ${arg.type})`}</ArgumentType>
          <ArgumentValue>{`${arg.value}`}</ArgumentValue>
        </ArgumentContent>,
      );
    }
  }

  if (entryMethod.type === Type.suspendYield) {
    const entrySuspendYield = entryMethod as EntrySuspendYield;
    argumentsList.push(
      <Header key={counter.next()} size="medium">
        <Header.Title title={`Yielded Value of type: ${entrySuspendYield.varType}`} />
      </Header>,
    );
    argumentsList.push(
      <LocationContent key={counter.next()}>{entrySuspendYield.value}</LocationContent>,
    );
  }

  return (
    <Content>
      {argumentsHeader}
      {argumentsList}
      <Header size="medium">
        <Header.Title title="Location" />
      </Header>
      <LocationContent>
        <Bold>File:</Bold> {entryMethod.source}
      </LocationContent>
      <LocationContent>
        <Bold>Line:</Bold> {entryMethod.lineno}
      </LocationContent>
    </Content>
  );
};

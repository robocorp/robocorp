import { Box, Header } from '@robocorp/components';
import { FC } from 'react';
import styled from 'styled-components';

import { Entry, EntryMethodBase, EntryReturn, EntrySuspendYield, Type } from '~/lib/types';
import { FormatHeaderActions, LocationContent, SourceAndLine, VariableValue } from './Common';
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

export const MethodComponent: FC<{ entry: Entry }> = (props) => {
  const entryMethod: EntryMethodBase | EntryReturn = props.entry as EntryMethodBase | EntryReturn;
  const argumentsList = [];
  let argumentsHeader = <></>;

  let counter = new Counter();

  if (entryMethod.type == Type.returnElement) {
    let entryReturn = entryMethod as EntryReturn;
    argumentsHeader = (
      <Header size="medium">
        <Header.Title title={'Return'} />
        <FormatHeaderActions />
      </Header>
    );
    argumentsList.push(
      <ArgumentContent key={counter.next()} className="argument">
        <ArgumentType>{`(type: ${entryReturn.varType})`}</ArgumentType>
        <VariableValue value={entryReturn.value}></VariableValue>
      </ArgumentContent>,
    );
  } else {
    let title = 'Arguments';
    if (
      entryMethod.type === Type.elseElement ||
      entryMethod.type === Type.ifElement ||
      entryMethod.type === Type.assertFailed
    ) {
      title = 'Variables';
    }

    if (entryMethod.arguments && entryMethod.arguments.length > 0) {
      argumentsHeader = (
        <Header size="medium">
          <Header.Title title={title} />
          <FormatHeaderActions />
        </Header>
      );
      for (const arg of entryMethod.arguments) {
        argumentsList.push(
          <ArgumentContent key={counter.next()} className="argument">
            <ArgumentName className="argumentName">{`${arg.name}`}</ArgumentName>
            <ArgumentType>{`(type: ${arg.type})`}</ArgumentType>
            <VariableValue value={arg.value}></VariableValue>
          </ArgumentContent>,
        );
      }
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
      <SourceAndLine source={entryMethod.source} lineno={entryMethod.lineno}></SourceAndLine>
    </Content>
  );
};

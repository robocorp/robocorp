import { Box, Header, Typography } from '@robocorp/components';
import { FC } from 'react';
import styled from 'styled-components';

import { Entry, EntryMethod } from '~/lib/types';
import { Bold, LocationContent } from './Common';

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
`;

const ArgumentType = styled(Box)`
  margin-left: ${({ theme }) => theme.space.$8};
  display: inline;
`;

const ArgumentValue = styled(Box)`
  margin-left: ${({ theme }) => theme.space.$12};
`;

export const Method: FC<{ entry: Entry }> = (props) => {
  const entryMethod: EntryMethod = props.entry as EntryMethod;
  const argumentsList = [];
  let argumentsHeader = <></>;
  if (entryMethod.arguments && entryMethod.arguments.length > 0) {
    argumentsHeader = (
      <Header size="medium">
        <Header.Title title="Arguments" />
      </Header>
    );
    let key = 0;
    for (const arg of entryMethod.arguments) {
      argumentsList.push(
        <ArgumentContent key={key} className="argument">
          <ArgumentName className="argumentName">{`${arg.name}`}</ArgumentName>
          <ArgumentType>{`(type: ${arg.type})`}</ArgumentType>
          <ArgumentValue>{`${arg.value}`}</ArgumentValue>
        </ArgumentContent>,
      );
      key += 1;
    }
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

import { FC } from 'react';
import { styled } from '@robocorp/theme';

import { Entry } from '~/lib/types';
import { Icon, Title, Toggle, Value } from './components';

type Props = {
  entry: Entry;
};

const Container = styled.div<{ depth: number }>`
  display: flex;
  flex: 1;
  padding-left: calc(${({ theme }) => theme.space.$24} * ${({ depth }) => depth});
  overflow: hidden;
`;

export const Step: FC<Props> = ({ entry }) => {
  const depth = entry.id.split('-').length - 1;

  return (
    <Container depth={depth} id={entry.id}>
      <Toggle entry={entry} />
      <Icon entry={entry} />
      <Title entry={entry} />
      <Value entry={entry} />
    </Container>
  );
};

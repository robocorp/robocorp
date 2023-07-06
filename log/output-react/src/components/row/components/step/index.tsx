import { FC } from 'react';
import { styled } from '@robocorp/theme';

import { Entry } from '~/lib/types';
import { Icon, Title, Toggle, Value } from './components';
import { useLogContext } from '~/lib';

type Props = {
  entry: Entry;
};

const Container = styled.div<{ depth: number; mode: 'compact' | 'sparse' }>`
  display: flex;
  flex: 1;
  padding-left: calc(
    ${({ theme, mode }) => (mode === 'compact' ? theme.space.$12 : theme.space.$24)} *
      ${({ depth }) => depth}
  );
  overflow: hidden;
`;

export const Step: FC<Props> = ({ entry }) => {
  let depth = entry.id.split('-').length - 1;
  if (depth > 20) {
    // Flatten after it's 20 levels deep.
    // (when it's too deep we can't really see it)
    depth = 20;
  }

  const { viewSettings } = useLogContext();

  return (
    <Container depth={depth} id={entry.id} mode={viewSettings.mode} className="rowEntryStep">
      <Toggle entry={entry} />
      <Icon entry={entry} />
      <Title entry={entry} />
      <Value entry={entry} />
    </Container>
  );
};

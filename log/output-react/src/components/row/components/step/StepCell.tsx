import { FC } from 'react';
import { styled } from '@robocorp/theme';

import { Entry } from '~/lib/types';
import { useLogContext } from '~/lib';
import { StepToggle } from './StepToggle';
import { StepIcon } from './StepIcon';
import { StepTitle } from './StepTitle';
import { StepValue } from './StepValue';

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

export const StepCell: FC<Props> = ({ entry }) => {
  let depth = entry.id.split('-').length - 1;
  if (depth > 20) {
    // Flatten after it's 20 levels deep.
    // (when it's too deep we can't really see it)
    depth = 20;
  }

  const { viewSettings } = useLogContext();

  return (
    <Container depth={depth} id={entry.id} mode={viewSettings.mode} className="rowEntryStep">
      <StepToggle entry={entry} />
      <StepIcon entry={entry} />
      <StepTitle entry={entry} />
      <StepValue entry={entry} />
    </Container>
  );
};

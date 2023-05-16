import { CSSProperties, FC, useCallback } from 'react';
import { styled } from '@robocorp/theme';
import { Tooltip } from '@robocorp/components';

import { formatDuration, formatLocation, useLogContext } from '~/lib';
import { Cell, Step } from './components';

type Props = {
  index: number;
  style: CSSProperties;
};

const Container = styled.div`
  cursor: pointer;
  display: flex;
  margin: 0 ${({ theme }) => theme.space.$24};
  width: calc(100% - ${({ theme }) => theme.space.$48}) !important;
  white-space: nowrap;
  border-bottom: 1px solid ${({ theme }) => theme.colors.border.subtle.color};

  &:hover {
    background: ${({ theme }) => theme.colors.background.subtle.light.hovered.color};
  }
`;

export const Row: FC<Props> = ({ index, ...rest }) => {
  const { filteredEntries, setActiveIndex, viewSettings } = useLogContext();
  const entry = filteredEntries.entries[index];

  const onToggle = useCallback(() => {
    setActiveIndex(index);
  }, [index]);

  return (
    <Container role="button" onClick={onToggle} onKeyPress={onToggle} {...rest} tabIndex={0}>
      <Step entry={entry} />
      {viewSettings.columns.location && (
        <Cell minWidth={180} cellClass="colLocation">
          <Tooltip text={formatLocation(entry)}>
            <span>{formatLocation(entry)}</span>
          </Tooltip>
        </Cell>
      )}
      {viewSettings.columns.duration && (
        <Cell minWidth={0} cellClass="colDuration">
          {formatDuration(entry)}
        </Cell>
      )}
    </Container>
  );
};

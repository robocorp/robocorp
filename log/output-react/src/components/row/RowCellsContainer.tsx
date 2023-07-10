import { CSSProperties, FC, useCallback } from 'react';
import { styled } from '@robocorp/theme';
import { Tooltip } from '@robocorp/components';

import { formatDuration, formatLocation, useLogContext } from '~/lib';
import { Cell } from './components/Cell';
import { StepCell } from './components/step/StepCell';
import { isInVSCode } from '~/vscode/vscodeComm';
import { getOpts } from '~/treebuild/options';

type Props = {
  index: number;
  style: CSSProperties;
};

const Container = styled.div<{ mode: 'compact' | 'sparse' }>`
  cursor: pointer;
  display: flex;
  margin: 0 ${({ theme, mode }) => (mode === 'compact' ? theme.space.$0 : theme.space.$24)};
  width: calc(
    100% - ${({ theme, mode }) => (mode === 'compact' ? theme.space.$0 : theme.space.$48)}
  ) !important;
  white-space: nowrap;
  border-bottom: 1px solid ${({ theme }) => theme.colors.border.subtle.color};

  &:hover {
    background: ${({ theme }) => theme.colors.background.subtle.light.hovered.color};
  }
`;

export const RowCellsContainer: FC<Props> = ({ index, ...rest }) => {
  const { filteredEntries, setActiveIndex, viewSettings } = useLogContext();
  const entry = filteredEntries.entries[index];

  const onToggle = useCallback(() => {
    setActiveIndex(index);
  }, [index]);

  let data: any = undefined;
  if (isInVSCode()) {
    const anyEntry = entry as any;
    if (anyEntry?.source && anyEntry?.lineno) {
      data = {
        source: anyEntry.source,
        lineno: anyEntry.lineno,
      };
    }
  }

  const onClickLocation = useCallback((data: any) => {
    if (data === undefined) {
      return;
    }
    const opts = getOpts();
    if (opts !== undefined && opts.onClickReference !== undefined) {
      opts.onClickReference(data);
    }
  }, []);

  return (
    <Container
      className="oneRow"
      role="button"
      onClick={onToggle}
      onKeyPress={onToggle}
      {...rest}
      tabIndex={0}
      mode={viewSettings.mode}
    >
      <StepCell entry={entry} />
      {viewSettings.columns.location && (
        <Cell minWidth={180} cellClass="colLocation">
          <span
            className={data !== undefined ? 'locationLink' : undefined}
            onClick={(ev) => {
              if (data !== undefined) {
                onClickLocation(data);
                ev.stopPropagation();
              }
            }}
          >
            {formatLocation(entry)}
          </span>
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

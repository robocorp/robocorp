import {
  CSSProperties,
  FC,
  useCallback,
  KeyboardEvent,
  useEffect,
  useRef,
  MouseEvent,
  FocusEvent,
  useState,
} from 'react';
import { styled } from '@robocorp/theme';

import { formatDuration, formatLocation, useLogContext } from '~/lib';
import { Cell } from './components/Cell';
import { StepCell } from './components/step/StepCell';
import { isInVSCode } from '~/vscode/vscodeComm';
import { getOpts } from '~/treebuild/options';
import { getNextMtime } from '~/lib/mtime';

type Props = {
  index: number;
  style: CSSProperties;
};

const Container = styled.div<{ mode: 'compact' | 'sparse' }>`
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
  const {
    filteredEntries,
    setDetailsIndex,
    viewSettings,
    focusIndex,
    setFocusIndex,
    toggleEntryExpandState,
  } = useLogContext();
  const entry = filteredEntries.entries[index];

  const [focused, setFocus] = useState<boolean>(false);
  const lastFocusMtime = useRef<number>(-1);

  const onKeyDown = useCallback(
    (event: KeyboardEvent) => {
      // When 'Enter' is used the details are shown and when
      // space is used the expanded state is toggled.
      if (event.key === 'Enter') {
        // setFocus(true);
        setFocusIndex({ indexAll: entry.entryIndexAll, mtime: getNextMtime() });
        setDetailsIndex({ indexAll: entry.entryIndexAll });
        event.stopPropagation();
      } else if (event.key === ' ') {
        event.stopPropagation();
        event.preventDefault(); // default would do a page down (scroll tree down).
        toggleEntryExpandState(entry.id);
      }
    },
    [index, entry],
  );

  const onBlur = useCallback(
    (event: FocusEvent) => {
      // When loosing focus make sure we remove the focus-related classes
      // (otherwise they can stick around).
      setFocus(false);
    },
    [entry],
  );

  const onClickRow = useCallback(
    (event: MouseEvent) => {
      setFocus(true);
      event.stopPropagation();
    },
    [index],
  );

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

  const containerRef = useRef(null);

  useEffect(() => {
    const curr: any = containerRef.current;
    if (curr !== undefined) {
      if (
        focusIndex &&
        lastFocusMtime.current !== focusIndex.mtime &&
        focusIndex.indexAll === entry.entryIndexAll
      ) {
        lastFocusMtime.current = focusIndex.mtime;
        setFocus(true);
        curr.focus();
      }
    }
  }, [containerRef, entry, focusIndex]);

  let className: string = 'oneRow';
  if (focused) {
    className += ' focus-visible';
  }

  return (
    <Container
      className={className}
      ref={containerRef}
      role="button"
      onClick={onClickRow}
      onKeyDown={onKeyDown}
      {...rest}
      tabIndex={0}
      mode={viewSettings.mode}
      onBlur={onBlur}
      // When tabbing 'focus-visible' and 'data-focus-visible-added'
      // are automatically set (by someone), so, we try to replicate
      // the same when doing it ourselves through the 'focused' state.
      {...(focused ? { 'data-focus-visible-added': '' } : {})}
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

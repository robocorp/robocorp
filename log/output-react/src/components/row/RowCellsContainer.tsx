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
import './components/step/step.css';

import { entryIdDepth, entryIdParent, formatDuration, formatLocation, useLogContext } from '~/lib';
import { Cell } from './components/Cell';
import { StepCell } from './components/step/StepCell';
import { isInVSCode } from '~/vscode/vscodeComm';
import { getOpts } from '~/treebuild/options';
import { doesEntryMatchIndex, setFocusIndexAndScroll } from '~/lib/selections';
import { getNextMtime } from '~/lib/mtime';
import { setScrollToItem } from '~/lib/scroll';

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

export const RowCellsContainer: FC<Props> = ({ index, style, ...rest }) => {
  const {
    entriesInfo,
    setDetailsIndex,
    viewSettings,
    focusIndex,
    setFocusIndex,
    selectionIndex,
    updateExpandState,
    scrollInfo,
  } = useLogContext();
  const entry = entriesInfo.treeEntries.entries[index];

  let [focused, setFocus] = useState<boolean>(false);

  const containerRef = useRef(null);

  useEffect(() => {
    const curr: any = containerRef.current;
    if (curr !== undefined) {
      if (focusIndex) {
        if (focusIndex.indexAll === entry.entryIndexAll) {
          // ok, matched focus index, but don't put focus unless the
          // focus has a higher mtime than the selection (because
          // we don't want to loose the focus from the selection).
          if (
            !selectionIndex ||
            (selectionIndex &&
              (selectionIndex.mtime === -1 || selectionIndex.mtime < focusIndex.mtime))
          ) {
            curr.focus();
          }
        }
      }
    }
  }, [containerRef.current, focusIndex?.indexAll === entry.entryIndexAll]);

  const onKeyDown = useCallback(
    (event: KeyboardEvent) => {
      // When 'Enter' is used the details are shown and when
      // space is used the expanded state is toggled.
      if (event.key === 'Enter') {
        if (containerRef.current) {
          (containerRef.current as any).focus();
        }
        setDetailsIndex({ indexAll: entry.entryIndexAll });
        event.stopPropagation();
        event.preventDefault();
      } else if (event.key === 'ArrowDown') {
        const goto = index + 1;
        if (goto < entriesInfo.treeEntries.entries.length) {
          setFocusIndexAndScroll(
            setFocusIndex,
            setScrollToItem,
            scrollInfo,
            entriesInfo,
            entriesInfo.treeEntries.entries[goto],
          );
        }
        event.stopPropagation();
        event.preventDefault();
      } else if (event.key === 'PageDown') {
        const goto = Math.min(index + 10, entriesInfo.treeEntries.entries.length - 1);
        setFocusIndexAndScroll(
          setFocusIndex,
          setScrollToItem,
          scrollInfo,
          entriesInfo,
          entriesInfo.treeEntries.entries[goto],
        );
        event.stopPropagation();
        event.preventDefault();
      } else if (event.key === 'ArrowUp') {
        const goto = index - 1;
        if (goto >= 0) {
          setFocusIndexAndScroll(
            setFocusIndex,
            setScrollToItem,
            scrollInfo,
            entriesInfo,
            entriesInfo.treeEntries.entries[goto],
          );
        }
        event.stopPropagation();
        event.preventDefault();
      } else if (event.key === 'PageUp') {
        const goto = Math.max(index - 10, 0);
        setFocusIndexAndScroll(
          setFocusIndex,
          setScrollToItem,
          scrollInfo,
          entriesInfo,
          entriesInfo.treeEntries.entries[goto],
        );
        event.stopPropagation();
        event.preventDefault();
      } else if (event.key === 'ArrowRight') {
        event.stopPropagation();
        event.preventDefault();
        updateExpandState(entry.id, 'expand', true);
      } else if (event.key === 'ArrowLeft') {
        event.stopPropagation();
        event.preventDefault();
        if (!updateExpandState(entry.id, 'collapse', true)) {
          const parentId = entryIdParent(entry.id);
          if (parentId !== undefined) {
            const parentEntry = entriesInfo.getEntryFromId(parentId);
            if (parentEntry !== undefined) {
              setFocusIndexAndScroll(
                setFocusIndex,
                setScrollToItem,
                scrollInfo,
                entriesInfo,
                parentEntry,
              );
            }
          }
        }
      } else if (event.key === ' ') {
        event.stopPropagation();
        event.preventDefault();
        updateExpandState(entry.id, 'toggle', true);
      }
    },
    [index, entry, entriesInfo.treeEntries, containerRef.current],
  );

  // Helper code to see what's cached.
  // useEffect(() => {
  //   console.log('use effect');
  //   // }, [index, entry, entriesInfo.treeEntries, containerRef.current]);
  // }, [entry]);

  const onBlur = useCallback(
    (event: FocusEvent) => {
      // When loosing focus make sure we remove the focus-related classes
      // (otherwise they can stick around until an update).
      setFocus(false);
    },
    [index, entry],
  );

  const onFocus = useCallback(
    (event: FocusEvent) => {
      setFocusIndex({ indexAll: entry.entryIndexAll, mtime: getNextMtime() });
      setFocus(true);
    },
    [index, entry],
  );

  const onClickRow = useCallback(
    (event: MouseEvent) => {
      if (containerRef.current) {
        (containerRef.current as any).focus();
      }
      event.stopPropagation();
    },
    [index, entry],
  );

  let isLocationLink = false;
  if (isInVSCode()) {
    const anyEntry = entry as any;
    if (anyEntry?.source && anyEntry?.lineno) {
      isLocationLink = true;
    }
  }

  const onClickLocation = useCallback(
    (ev: MouseEvent) => {
      let data: any = undefined;
      if (isLocationLink) {
        const anyEntry = entry as any;
        if (anyEntry?.source && anyEntry?.lineno) {
          data = {
            source: anyEntry.source,
            lineno: anyEntry.lineno,
          };
        }
      }

      if (data === undefined) {
        return;
      }
      const opts = getOpts();
      if (opts !== undefined && opts.onClickReference !== undefined) {
        opts.onClickReference(data);
      }
    },
    [entry],
  );

  let className: string = 'oneRow';

  if (focused || doesEntryMatchIndex(entry, focusIndex)) {
    className += ' focus-visible';
  }

  if (doesEntryMatchIndex(entry, selectionIndex)) {
    className += ` selection-visible-${viewSettings.theme}`;
  }

  return (
    <Container
      className={className}
      ref={containerRef}
      role="button"
      onClick={onClickRow}
      onKeyDown={onKeyDown}
      style={style}
      tabIndex={0}
      mode={viewSettings.mode}
      onFocus={onFocus}
      onBlur={onBlur}
      // When tabbing 'focus-visible' and 'data-focus-visible-added'
      // are automatically set (by someone), so, we try to replicate
      // the same when doing it ourselves through the 'focused' state.
      {...(focused ? { 'data-focus-visible-added': '' } : {})}
      {...{ 'data-focus-entry-id': entry.id }}
    >
      <StepCell entry={entry} />
      {viewSettings.columns.location && (
        <Cell minWidth={180} cellClass="colLocation">
          <span className={isLocationLink ? 'locationLink' : undefined} onClick={onClickLocation}>
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

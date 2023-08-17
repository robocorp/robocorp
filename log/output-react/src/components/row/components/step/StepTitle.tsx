import { FC, MouseEvent, useCallback, useMemo, useState } from 'react';
import { Box, Tooltip, Typography } from '@robocorp/components';
import './step.css';

import {
  Entry,
  EntryMethod,
  EntryTask,
  Type,
  EntryVariable,
  EntryGenerator,
  EntryUntrackedGenerator,
  EntryResumeYield,
  EntryResumeYieldFrom,
  EntrySuspendYield,
  EntrySuspendYieldFrom,
  EntryThreadDump,
  EntryIf,
  EntryElse,
  EntryAssertFailed,
} from '~/lib/types';
import { truncateString, useLogContext } from '~/lib';
import { IconDoubleChevronDown, IconDoubleChevronUp } from '@robocorp/icons/iconic';

type Props = {
  entry: Entry;
};

export const getTitle = (entry: Entry): string => {
  switch (entry.type) {
    case Type.task:
      return (entry as EntryTask).name;
    case Type.processSnapshot:
      return '';
    case Type.threadDump:
      return `Thread Stack: ${(entry as EntryThreadDump).threadName}`;
    case Type.generator:
      return `${(entry as EntryGenerator).name} (enter generator)`;
    case Type.untrackedGenerator:
      return `${(entry as EntryUntrackedGenerator).name} (generator lifecycle untracked)`;
    case Type.resumeYield:
      return `${(entry as EntryResumeYield).name} (resume generator)`;
    case Type.resumeYieldFrom:
      return `${(entry as EntryResumeYieldFrom).name} (resume generator)`;
    case Type.suspendYield:
      return `${(entry as EntrySuspendYield).name} (suspend generator)`;
    case Type.suspendYieldFrom:
      return `${(entry as EntrySuspendYieldFrom).name} (suspend generator)`;
    case Type.method:
      return (entry as EntryMethod).name;
    case Type.assertFailed:
      return (entry as EntryAssertFailed).name;
    case Type.ifElement:
      return `Entered "${(entry as EntryIf).name}"`;
    case Type.elseElement:
      return `Entered "${(entry as EntryElse).name}"`;
    case Type.returnElement:
      return `Return`;
    case Type.continueElement:
      return `Continue`;
    case Type.breakElement:
      return `Break`;
    case Type.log:
      return ''; // the log type is added in the icon.
    case Type.console:
      return ''; // Not much to add...
    case Type.variable:
      return (entry as EntryVariable).name;
    case Type.exception:
      return ''; // the type is added in the icon.
    // return (entry as EntryException).excType;
    default:
      console.log('TODO: Provide getTitle for', entry);
      return 'TODO: provide getTitle';
  }
};

export const StepTitle: FC<Props> = ({ entry }) => {
  const title = useMemo(() => {
    const ret = getTitle(entry);
    if (!ret) {
      return ret;
    }
    return truncateString(ret, 80);
  }, [entry]);

  const { setDetailsIndex, updateExpandState, entriesInfo } = useLogContext();
  const [hover, setHover] = useState(false);

  const onClickShowDetails = useCallback(
    (e: MouseEvent) => {
      e.stopPropagation();
      setDetailsIndex({ indexAll: entry.entryIndexAll });
    },
    [entry, setDetailsIndex],
  );

  const onMouseEnter = useCallback((e: MouseEvent) => {
    setHover(true);
  }, []);

  const onMouseLeave = useCallback((e: MouseEvent) => {
    setHover(false);
  }, []);

  const onClickExpandSubtree = useCallback(
    (e: MouseEvent) => {
      e.stopPropagation();
      e.preventDefault();
      updateExpandState(entry.id, 'expandSubTree', true);
    },
    [entry, updateExpandState],
  );

  const onClickCollapseSubtree = useCallback(
    (e: MouseEvent) => {
      e.stopPropagation();
      e.preventDefault();
      updateExpandState(entry.id, 'collapseSubTree', false);
    },
    [entry, updateExpandState],
  );

  if (!title) {
    return <></>;
  }

  return (
    <Box
      minWidth={0}
      className="entryName"
      onClick={onClickShowDetails}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
      style={{ cursor: 'pointer' }}
    >
      <Typography mr="$32" lineHeight="$32" variant="body.small" fontWeight="medium" truncate={1}>
        {title}
        {hover && entriesInfo.treeEntries.entriesWithChildren.has(entry.id) ? (
          <>
            <Tooltip text="Collapse subtree">
              <span onClick={onClickCollapseSubtree} className="collapseButton">
                <IconDoubleChevronUp color="magenta60" size={'medium'} />
              </span>
            </Tooltip>
            <Tooltip text="Expand subtree">
              <span onClick={onClickExpandSubtree} className="expandButton">
                <IconDoubleChevronDown color="magenta60" size={'medium'} />
              </span>
            </Tooltip>
          </>
        ) : (
          <></>
        )}
      </Typography>
    </Box>
  );
};

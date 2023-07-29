import { FC, useCallback, MouseEvent, KeyboardEvent } from 'react';
import { Box } from '@robocorp/components';
import { styled } from '@robocorp/theme';

import { Entry } from '~/lib/types';
import { useLogContext } from '~/lib';

type Props = {
  entry: Entry;
};

const Button = styled.button`
  padding: 0 ${({ theme }) => theme.space.$4} 0 ${({ theme }) => theme.space.$4};
  background: none;

  svg path {
    fill: ${({ theme }) => theme.colors.content.subtle.light.color};
  }

  &:hover {
    svg path {
      fill: ${({ theme }) => theme.colors.content.subtle.light.hovered.color};
    }
  }
`;

export const StepToggle: FC<Props> = ({ entry }) => {
  const { entriesInfo, isExpanded, updateExpandState } = useLogContext();

  const expanded = isExpanded(entry.id);

  const onClickToggleExpand = useCallback(
    (e: MouseEvent) => {
      e.stopPropagation();
      updateExpandState(entry.id, 'toggle', true);
    },
    [entry.id],
  );

  const onKeyDownIgnore = useCallback(
    (event: KeyboardEvent) => {
      if (event.key === 'Enter') {
        // When the button has focus and the user presses enter, we'll automatically have
        // an onClick event (so, that's where the onClick will toggle the entry), but also
        // we don't want the parent to have the same event (as that'd make the details
        // be seen for the item), so, we have to stop the propagation of this event.
        event.stopPropagation();
      }
    },
    [entry.id],
  );

  // Add the expand/collapse if we have a parent or no icon if it cannot be expanded.
  if (!entriesInfo.treeEntries.entriesWithChildren.has(entry.id)) {
    return <Box className="noExpand" width="$20" height="100%" flexShrink={0} />;
  }

  return (
    <Button
      onClick={onClickToggleExpand}
      onKeyDown={onKeyDownIgnore}
      aria-label="Toggle item"
      className="toggleExpand"
      tabIndex={-1}
    >
      {expanded ? (
        <svg width="12" height="12" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M10.594 3.959A.75.75 0 0 0 10 2.75H1.5a.75.75 0 0 0-.593 1.209l4.25 5.5a.75.75 0 0 0 1.186 0l4.25-5.5Z" />
        </svg>
      ) : (
        <svg width="12" height="12" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M3.459 1.407A.75.75 0 0 0 2.25 2v8.5a.75.75 0 0 0 1.209.594l5.5-4.25a.75.75 0 0 0 0-1.187l-5.5-4.25Z" />
        </svg>
      )}
    </Button>
  );
};

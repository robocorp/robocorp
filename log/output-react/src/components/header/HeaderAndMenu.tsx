import { ChangeEvent, FC, KeyboardEvent, useCallback, useEffect, useState } from 'react';
import {
  Badge,
  Box,
  Button,
  Header as BaseHeader,
  Input,
  Menu,
  BadgeVariant,
  Tooltip,
  Select,
  SelectItem,
} from '@robocorp/components';
import { IconCloseSmall, IconFilter, IconSettings, IconTerminal } from '@robocorp/icons';
import { IconInformation, IconSearch } from '@robocorp/icons/iconic';
import {
  RunIdsAndLabel,
  RunInfo,
  SearchInfoRequest,
  createDefaultSearchInfoRequest,
  formatTimeInSeconds,
  useLogContext,
} from '~/lib';
import { CustomActions } from '~/lib/CustomActions';
import { isInVSCode, onChangeCurrentRunId } from '~/vscode/vscodeComm';
import { SUPPORTED_VERSION } from '~/treebuild/decoder';
import { StatusLevel } from '~/lib/types';
import { getNextMtime, updateMtime } from '~/lib/mtime';
import { clearSelection } from '~/lib/selections';
import { setScrollToItem } from '~/lib/scroll';
import { makeSearch } from '~/lib/search';

type Props = {
  runInfo: RunInfo;
  runIdsAndLabel: RunIdsAndLabel;
};

export const HeaderAndMenu: FC<Props> = ({ runInfo, runIdsAndLabel }) => {
  const [searchInfoRequest, setSearchInfoRequest] = useState<SearchInfoRequest>(
    createDefaultSearchInfoRequest(),
  );
  const {
    viewSettings,
    setSelectionIndex,
    setViewSettings,
    setDetailsIndex,
    entriesInfo,
    selectionIndex,
    focusIndex,
    updateExpandState,
    scrollInfo,
  } = useLogContext();

  useEffect(() => {
    if (!searchInfoRequest.searchValue) {
      // If there's no search value, clear the selection.
      clearSelection(selectionIndex, setSelectionIndex);
      return;
    }
    if (updateMtime('searchApplied', searchInfoRequest.requestMTime)) {
      const searchResult = makeSearch(entriesInfo, searchInfoRequest, selectionIndex, focusIndex);
      if (searchResult) {
        // The search must auto-expand parents and set the current selection.
        const parentsToExpand = searchResult.expandParentIds;
        updateExpandState(parentsToExpand, 'expand', false);
        const selected = searchResult.selectedEntry;
        if (selected) {
          setSelectionIndex({ indexAll: selected.entryIndexAll, mtime: getNextMtime() });
          setScrollToItem(scrollInfo, entriesInfo, selected);
          return;
        }
      }
      // If it hasn't returned we need to clear the selection.
      clearSelection(selectionIndex, setSelectionIndex);
    }
  }, [entriesInfo, selectionIndex, searchInfoRequest.requestMTime]);

  const onFilterChange = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    setSearchInfoRequest((curr: SearchInfoRequest): SearchInfoRequest => {
      return {
        ...curr,
        searchValue: e.target.value,
        direction: 'forward',
        incremental: true,
        requestMTime: getNextMtime(),
      };
    });
  }, []);

  const onFilterReset = useCallback(() => {
    setSearchInfoRequest(createDefaultSearchInfoRequest());
  }, []);

  const onKeyDown = useCallback((e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key == 'Escape') {
      setSearchInfoRequest(createDefaultSearchInfoRequest());
    } else if (e.key == 'Enter') {
      if (e.shiftKey) {
        setSearchInfoRequest((curr: SearchInfoRequest): SearchInfoRequest => {
          return {
            ...curr,
            direction: 'backward',
            incremental: false,
            requestMTime: getNextMtime(),
          };
        });
      } else {
        setSearchInfoRequest((curr: SearchInfoRequest): SearchInfoRequest => {
          return {
            ...curr,
            direction: 'forward',
            incremental: false,
            requestMTime: getNextMtime(),
          };
        });
      }
    }
  }, []);

  const onToggleLocation = useCallback(() => {
    setViewSettings((curr) => ({
      ...curr,
      columns: { ...curr.columns, location: !curr.columns.location },
    }));
  }, []);

  const onToggleDuration = useCallback(() => {
    setViewSettings((curr) => ({
      ...curr,
      columns: { ...curr.columns, duration: !curr.columns.duration },
    }));
  }, []);

  const onToggleTheme = useCallback(() => {
    setViewSettings((curr) => ({
      ...curr,
      theme: curr.theme === 'dark' ? 'light' : 'dark',
    }));
  }, []);

  const onToggleMode = useCallback(() => {
    setViewSettings((curr) => ({
      ...curr,
      mode: curr.mode === 'compact' ? 'sparse' : 'compact',
    }));
  }, []);

  const onToggleDebugLevel = useCallback(() => {
    setViewSettings((curr) => ({
      ...curr,
      treeFilterInfo: { showInTree: curr.treeFilterInfo.showInTree ^ StatusLevel.debug },
    }));
  }, []);

  const onToggleInfoLevel = useCallback(() => {
    setViewSettings((curr) => ({
      ...curr,
      treeFilterInfo: { showInTree: curr.treeFilterInfo.showInTree ^ StatusLevel.info },
    }));
  }, []);

  const onToggleWarnLevel = useCallback(() => {
    setViewSettings((curr) => ({
      ...curr,
      treeFilterInfo: { showInTree: curr.treeFilterInfo.showInTree ^ StatusLevel.warn },
    }));
  }, []);

  const onToggleErrorLevel = useCallback(() => {
    setViewSettings((curr) => ({
      ...curr,
      treeFilterInfo: { showInTree: curr.treeFilterInfo.showInTree ^ StatusLevel.error },
    }));
  }, []);

  let variant: BadgeVariant = 'magenta';
  let label: string = '<INTERNAL MSG>: set label for: ' + runInfo.status;

  let partLabel: string | undefined = undefined;
  let partTooltipText: string | undefined = undefined;
  if (runInfo.firstPart != -1) {
    if (runInfo.firstPart > 1) {
      partLabel = `Log parts rotated out (showing part ${runInfo.firstPart} onwards).`;
      partTooltipText = `Note that the log contents being shown do not have contents from the start of the run. The logged contents prior to part ${runInfo.firstPart} were rotated out.`;
    }
  }

  switch (runInfo.status) {
    case 'ERROR':
      label = 'Run Failed';
      variant = 'danger';
      break;
    case 'PASS':
      label = 'Run Passed';
      variant = 'success';
      break;
    case 'UNSET':
      label = 'Unfinished ...';
      variant = 'magenta';
      break;
  }
  const time: string = runInfo.time;
  const timeDelta: number | undefined = runInfo.finishTimeDeltaInSeconds;
  let timeDescription = '';
  if (time && time.length > 0) {
    timeDescription = time;
    if (timeDelta !== undefined) {
      timeDescription += ' — took: ' + formatTimeInSeconds(timeDelta);
    }
  }

  const onClickInformation = useCallback(() => {
    setDetailsIndex('information');
  }, []);
  const onClickTerminal = useCallback(() => {
    setDetailsIndex('terminal');
  }, []);

  let px = '$24';
  let pt = '$32';
  if (viewSettings.mode === 'compact') {
    px = '$4';
    pt = '$0';
  }

  let runItems: SelectItem[] = [];
  let currSelectValue: string | undefined = runIdsAndLabel.currentRunId;
  for (const [runId, label] of runIdsAndLabel.allRunIdsToLabel.entries()) {
    runItems.push({ value: runId, label: label });
  }

  return (
    <Box px={px} pt={pt} pb="0" backgroundColor="background.primary" id="base-header">
      <BaseHeader className="base-header-container" size="medium">
        <BaseHeader.Title title={runInfo.description}>
          <Badge variant={variant} label={label} size="small" id="runStatusBadge" />
          {partLabel !== undefined ? (
            <Tooltip text={partTooltipText}>
              <Badge variant={'magenta'} label={partLabel} size="small" id="runPartBadge" />
            </Tooltip>
          ) : (
            <></>
          )}
          {runInfo.versionTooNew ? (
            <Tooltip
              text={`The log format version found is ${runInfo.version}.
                
                 The max version expected by the log (HTML) viewer is: ${SUPPORTED_VERSION}.
                
                 Note: the viewer will still attempt to load the values, but the visualization may break or may show wrong information.`}
            >
              <Badge
                variant={'danger'}
                label={'Log version too new. Please upgrade the log (HTML) viewer!'}
                size="small"
                id="versionTooNew"
              />
            </Tooltip>
          ) : (
            <></>
          )}
          <Tooltip text="General Information">
            <Button
              icon={IconInformation}
              aria-label="Information"
              size="small"
              variant="secondary"
              onClick={onClickInformation}
            ></Button>
          </Tooltip>
          <Tooltip text="Terminal Output">
            <Button
              icon={IconTerminal}
              aria-label="Terminal"
              size="small"
              variant="secondary"
              onClick={onClickTerminal}
            ></Button>
          </Tooltip>
        </BaseHeader.Title>
        {viewSettings.mode === 'compact' ? (
          <></>
        ) : (
          <BaseHeader.Description>{timeDescription}</BaseHeader.Description>
        )}
        <CustomActions>
          <Menu
            trigger={
              <Button
                icon={IconSettings}
                variant="secondary"
                aria-label="Settings"
                title="Settings (theme, layout, columns)"
              />
            }
            leaveMenuOpenOnItemSelect
          >
            <Menu.Title>Theme</Menu.Title>
            <Menu.Checkbox checked={viewSettings.theme === 'dark'} onClick={onToggleTheme}>
              Dark
            </Menu.Checkbox>
            <Menu.Checkbox checked={viewSettings.theme === 'light'} onClick={onToggleTheme}>
              Light
            </Menu.Checkbox>
            <Menu.Title>Layout</Menu.Title>
            <Menu.Checkbox checked={viewSettings.mode === 'compact'} onClick={onToggleMode}>
              Compact
            </Menu.Checkbox>
            <Menu.Checkbox checked={viewSettings.mode === 'sparse'} onClick={onToggleMode}>
              Sparse
            </Menu.Checkbox>
            <Menu.Title>Columns</Menu.Title>
            <Menu.Checkbox checked={viewSettings.columns.location} onClick={onToggleLocation}>
              Location
            </Menu.Checkbox>
            <Menu.Checkbox checked={viewSettings.columns.duration} onClick={onToggleDuration}>
              Duration
            </Menu.Checkbox>
          </Menu>
          <Menu
            trigger={
              <Button
                icon={IconFilter}
                variant="secondary"
                aria-label="Filters"
                title="Apply filters to show only the accepted items in the tree."
              />
            }
            leaveMenuOpenOnItemSelect
          >
            <Menu.Title>Filter</Menu.Title>
            <Menu.Checkbox
              checked={(viewSettings.treeFilterInfo.showInTree & StatusLevel.debug) !== 0}
              onClick={onToggleDebugLevel}
            >
              Debug
            </Menu.Checkbox>
            <Menu.Checkbox
              checked={(viewSettings.treeFilterInfo.showInTree & StatusLevel.info) !== 0}
              onClick={onToggleInfoLevel}
            >
              Information
            </Menu.Checkbox>
            <Menu.Checkbox
              checked={(viewSettings.treeFilterInfo.showInTree & StatusLevel.warn) !== 0}
              onClick={onToggleWarnLevel}
            >
              Warning
            </Menu.Checkbox>
            <Menu.Checkbox
              checked={(viewSettings.treeFilterInfo.showInTree & StatusLevel.error) !== 0}
              onClick={onToggleErrorLevel}
            >
              Error
            </Menu.Checkbox>
          </Menu>
          <Input
            value={searchInfoRequest.searchValue}
            onChange={onFilterChange}
            onKeyDown={onKeyDown}
            aria-label="Search logs"
            placeholder="Search logs"
            iconLeft={IconSearch}
            iconRight={searchInfoRequest.searchValue.length > 0 ? IconCloseSmall : undefined}
            onIconRightClick={onFilterReset}
            iconRightLabel="Reset filter"
          />
          {isInVSCode() ? (
            <Select
              value={currSelectValue}
              items={runItems}
              onChange={onChangeCurrentRunId}
              noItemsFound="No runs available"
              aria-label="Select Run"
            ></Select>
          ) : (
            <></>
          )}
        </CustomActions>
      </BaseHeader>
    </Box>
  );
};

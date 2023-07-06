import { ChangeEvent, FC, useCallback } from 'react';
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
import { IconCloseSmall, IconTerminal } from '@robocorp/icons';
import { IconInformation, IconSearch, IconSettingsSliders } from '@robocorp/icons/iconic';
import { RunIdsAndLabel, RunInfo, formatTimeInSeconds, useLogContext } from '~/lib';
import { CustomActions } from '~/lib/CustomActions';
import { isInVSCode, onChangeCurrentRunId } from '~/vscode/vscodeComm';

type Props = {
  filter: string;
  setFilter: (filter: string) => void;
  runInfo: RunInfo;
  runIdsAndLabel: RunIdsAndLabel;
};

export const Header: FC<Props> = ({ filter, setFilter, runInfo, runIdsAndLabel }) => {
  const { viewSettings, setViewSettings, setActiveIndex } = useLogContext();

  const onFilterChange = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    setFilter(e.target.value);
  }, []);

  const onFilterReset = useCallback(() => {
    setFilter('');
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

  let variant: BadgeVariant = 'magenta';
  let label: string = 'TODO: set label for: ' + runInfo.status;

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
    setActiveIndex('information');
  }, []);
  const onClickTerminal = useCallback(() => {
    setActiveIndex('terminal');
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
              <Button icon={IconSettingsSliders} variant="secondary" aria-label="Toggle option" />
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
          <Input
            value={filter}
            onChange={onFilterChange}
            aria-label="Search logs"
            placeholder="Search logs"
            iconLeft={IconSearch}
            iconRight={filter.length > 0 ? IconCloseSmall : undefined}
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

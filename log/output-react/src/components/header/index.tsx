import { ChangeEvent, FC, useCallback } from 'react';
import {
  Badge,
  Box,
  Button,
  Header as BaseHeader,
  Input,
  Menu,
  BadgeVariant,
} from '@robocorp/components';
import { IconCloseSmall } from '@robocorp/icons';
import { IconSearch, IconSettingsSliders } from '@robocorp/icons/iconic';
import { RunInfo, formatTimeInSeconds, useLogContext } from '~/lib';

type Props = {
  filter: string;
  setFilter: (filter: string) => void;
  runInfo: RunInfo;
};

export const Header: FC<Props> = ({ filter, setFilter, runInfo }) => {
  const { viewSettings, setViewSettings } = useLogContext();

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

  let variant: BadgeVariant = 'magenta';
  let label: string = 'TODO: set label for: ' + runInfo.status;
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
  return (
    <Box px="$24" pt="$32" pb="0" backgroundColor="background.primary" id="base-header">
      <BaseHeader size="medium">
        <BaseHeader.Title title={runInfo.description}>
          <Badge variant={variant} label={label} size="small" id="runStatusBadge" />
        </BaseHeader.Title>
        <BaseHeader.Description>{timeDescription}</BaseHeader.Description>
        <BaseHeader.Actions>
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
        </BaseHeader.Actions>
      </BaseHeader>
    </Box>
  );
};

import { Drawer, Header } from '@robocorp/components';
import { FC, useCallback, useMemo } from 'react';
import { logError } from '~/lib/helpers';
import {
  ActionRunConsole,
  DefinitionList,
  Duration,
  StatusBadge,
  Timestamp,
  Code,
} from '~/components';
import { useActionRunsContext } from './context';

export const ActionRunDetails: FC = () => {
  const { showRun: run, setShowRun } = useActionRunsContext();

  const onClose = useCallback(() => {
    setShowRun(undefined);
  }, []);

  const inputs = useMemo(() => {
    try {
      if (!run) {
        return '';
      }

      const output = Object.entries(JSON.parse(run.inputs));

      if (output.length === 0) {
        return 'No inputs sent';
      }
      return JSON.stringify(JSON.parse(run.inputs), null, 4);
    } catch (err) {
      logError(err);
      return `Error collecting inputs: ${JSON.stringify(err)}`;
    }
  }, [run?.inputs]);

  if (!run) {
    return '';
  }

  return (
    <Drawer onClose={onClose} width={760} open>
      <Drawer.Header>
        <Drawer.Header.Title title={run.action?.name} />
        <Drawer.Header.Description>
          <StatusBadge status={run.status} size="small" />
        </Drawer.Header.Description>
      </Drawer.Header>
      <Drawer.Content>
        <Header size="small">
          <Header.Title title="Run information" />
        </Header>
        <DefinitionList>
          <DefinitionList.Key>Started at:</DefinitionList.Key>
          <DefinitionList.Value>
            <Timestamp timestamp={run.start_time} />
          </DefinitionList.Value>
          <DefinitionList.Key>Run time:</DefinitionList.Key>
          <DefinitionList.Value>
            <Duration seconds={run.run_time} />
          </DefinitionList.Value>
        </DefinitionList>

        <Header size="small">
          <Header.Title title="Run input" />
        </Header>
        <Code lang="json" aria-label="Run input" value={inputs} />

        <Header size="small">
          <Header.Title title="Run result" />
        </Header>
        <Code aria-label="Run input" value={run.result || ''} />

        <Header size="small">
          <Header.Title title="Console output" />
        </Header>

        <ActionRunConsole runId={run.id} />
      </Drawer.Content>
    </Drawer>
  );
};

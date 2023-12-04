import {Drawer } from '@robocorp/components';
import { FC, useCallback } from 'react';
import { Box } from '@robocorp/components';
import { NOT_RUN, RUNNING, PASSED, FAILED, StatusBadge, useActionRunsContext } from './ActionRuns';
import {
  Counter,
  parseDateisoformatToLocalTimezoneStr,
  logError,
  formatTimeInSeconds,
} from '~/lib/helpers';
import { MarginBotton, Variable, VariableHeaderBig, VariableHeaderContent } from './Common';
import { ActionRawDetails } from './ActionDetails';

export const ActionRunDetails: FC<{}> = ({}) => {
  const { showRun, setShowRun } = useActionRunsContext();
  const onClose = useCallback(() => {
    setShowRun(undefined);
  }, []);

  if (showRun === undefined) {
    return <></>;
  }

  const counter = new Counter();
  const contents = [];

  contents.push(
    <VariableHeaderBig key={counter.next()}>
      <VariableHeaderContent>{'Run Information'}</VariableHeaderContent>
    </VariableHeaderBig>,
  );

  try {
    const inputs = Object.entries(JSON.parse(showRun.inputs));

    if (inputs.length === 0) {
      contents.push(<Variable key={counter.next()} name={'Inputs'} value={'No inputs sent'} />);
    } else {
      for (const [key, value] of inputs) {
        contents.push(<Variable key={counter.next()} name={`Input: ${key}`} value={'' + value} />);
      }
    }
  } catch (err) {
    logError(err);
    contents.push(<Box>{`Error collecting inputs: ${JSON.stringify(err)}`}</Box>);
  }

  if (showRun.status == NOT_RUN) {
    contents.push(
      <Variable
        key={counter.next()}
        name={`State`}
        value={
          <>
            <StatusBadge rowData={showRun}></StatusBadge>
            {' Run still not running.'}
          </>
        }
      />,
    );
  } else if (showRun.status == RUNNING) {
    contents.push(
      <Variable
        key={counter.next()}
        name={`State`}
        value={
          <>
            <StatusBadge rowData={showRun}></StatusBadge>
            {' Run is currently running and still has not finished.'}
          </>
        }
      />,
    );
  } else if (showRun.status == PASSED) {
    contents.push(
      <Variable
        key={counter.next()}
        name={`State`}
        value={
          <>
            <StatusBadge rowData={showRun}></StatusBadge>
            {' Run finished successfully.'}
          </>
        }
      />,
    );
    contents.push(<Variable key={counter.next()} name={`Result`} value={showRun.result} />);
  } else if (showRun.status == FAILED) {
    contents.push(
      <Variable
        key={counter.next()}
        name={`State`}
        value={
          <>
            <StatusBadge rowData={showRun}></StatusBadge>
            {' Run finished with some error.'}
          </>
        }
      />,
    );
    contents.push(<Variable key={counter.next()} name={`Result`} value={showRun.error_message} />);
  }

  let finishedTimeInfo = '';
  if (showRun.status == PASSED || showRun.status == FAILED) {
    if (showRun.run_time !== undefined) {
      const runTime = formatTimeInSeconds(showRun.run_time || 0);
      finishedTimeInfo = ` -- finished in ${runTime}`;
    }
  }

  contents.push(
    <VariableHeaderBig key={counter.next()}>
      <VariableHeaderContent>{'Action Information'}</VariableHeaderContent>
    </VariableHeaderBig>,
  );
  contents.push(<ActionRawDetails key={counter.next()} action={showRun.action}></ActionRawDetails>);

  const startTime = parseDateisoformatToLocalTimezoneStr(showRun.start_time);
  const title = (
    <>
      {`${showRun.action?.name || '<unable to get name>'} `}
      <StatusBadge rowData={showRun} />
    </>
  );
  return (
    <Drawer passive onClose={onClose} width={1024} open={true}>
      <Drawer.Header>
        <Drawer.Header.Title title={title} />
        <Drawer.Header.Description>{`Run started at: ${startTime}  ${finishedTimeInfo}`}</Drawer.Header.Description>
      </Drawer.Header>
      <Drawer.Content>
        {contents}
        <MarginBotton />
      </Drawer.Content>
    </Drawer>
  );
};

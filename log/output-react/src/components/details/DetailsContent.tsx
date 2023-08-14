import { FC } from 'react';
import { Box } from '@robocorp/components';

import { Entry, Type } from '~/lib/types';
import { ExceptionComponent, ThreadDumpComponent } from './components/ExceptionComponent';
import { LogComponent } from './components/LogComponent';
import { MethodComponent } from './components/MethodComponent';
import { TaskComponent } from './components/TaskComponent';
import { VariableComponent } from './components/VariableComponent';

export const Todo: FC<{ entry: Entry }> = (props) => {
  return <>TODO: provide details for {props.entry.type}</>;
};

export const Empty: FC<{ entry: Entry }> = (props) => {
  return <></>;
};

const getContentComponent = (type: Type) => {
  switch (type) {
    case Type.method:
    case Type.generator:
    case Type.untrackedGenerator:
    case Type.resumeYield:
    case Type.resumeYieldFrom:
    case Type.suspendYield:
    case Type.ifElement:
    case Type.elseElement:
    case Type.returnElement:
    case Type.continueElement:
    case Type.breakElement:
    case Type.assertFailed:
      return MethodComponent;
    case Type.exception:
      return ExceptionComponent;
    case Type.threadDump:
      return ThreadDumpComponent;
    case Type.variable:
      return VariableComponent;
    case Type.task:
      return TaskComponent;
    case Type.log:
    case Type.console:
      return LogComponent;
    case Type.processSnapshot:
      return Empty;
    default:
      return Todo;
  }
};

export const DetailsContent: FC<{ entry: Entry }> = ({ entry }) => {
  const Component = getContentComponent(entry.type);

  return (
    // <Box p="$32" borderColor="border.inversed" borderRadius="$16" margin="$8">
    <Box p="$16" margin="$8">
      <Component entry={entry} />
    </Box>
  );
};

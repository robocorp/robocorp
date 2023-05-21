import { FC } from 'react';
import { Box, Drawer } from '@robocorp/components';

import { Entry, Type } from '~/lib/types';
import { ExceptionComponent } from './components/ExceptionComponent';
import { Method } from './components/Method';
import { VariableComponent } from './components/VariableComponent';
import { TaskComponent } from './components/TaskComponent';
import { LogComponent } from './components/LogComponent';

export const Todo: FC<{ entry: Entry }> = (props) => {
  return <>Todo: provide details for {props.entry.type}</>;
};

const getContentComponent = (type: Type) => {
  switch (type) {
    case Type.method:
    case Type.generator:
    case Type.untrackedGenerator:
    case Type.resumeYield:
    case Type.resumeYieldFrom:
    case Type.suspendYield:
    case Type.suspendYieldFrom:
      return Method;
    case Type.exception:
      return ExceptionComponent;
    case Type.variable:
      return VariableComponent;
    case Type.task:
      return TaskComponent;
    case Type.log:
      return LogComponent;
    default:
      return Todo;
  }
};

export const Content: FC<{ entry: Entry }> = ({ entry }) => {
  const Component = getContentComponent(entry.type);

  return (
    <Box p="$32" borderColor="border.inversed" borderRadius="$16" margin="$8">
      <Component entry={entry} />
    </Box>
  );
};

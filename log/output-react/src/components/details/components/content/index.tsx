import { FC } from 'react';
import { Box, Drawer } from '@robocorp/components';

import { Entry, Type } from '~/lib/types';
import { ExceptionComponent } from './components/ExceptionComponent';
import { Method } from './components/Method';
import { VariableComponent } from './components/VariableComponent';
import { TaskComponent } from './components/TaskComponent';

export const Todo: FC<{ entry: Entry }> = (props) => {
  return <>Todo: support {props.entry.type}</>;
};

const getContentComponent = (type: Type) => {
  switch (type) {
    case Type.method:
      return Method;
    case Type.exception:
      return ExceptionComponent;
    case Type.variable:
      return VariableComponent;
    case Type.task:
      return TaskComponent;
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

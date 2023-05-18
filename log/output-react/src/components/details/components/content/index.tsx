import { FC } from 'react';
import { Drawer } from '@robocorp/components';

import { Entry, Type } from '~/lib/types';
import { ErrorComponent } from './components/ErrorComponent';
import { Method } from './components/Method';

export const Todo: FC<{ entry: Entry }> = (props) => {
  return <>Todo: support {props.entry.type}</>;
};

const getContentComponent = (type: Type) => {
  switch (type) {
    case Type.method:
      return Method;
    case Type.error:
      return ErrorComponent;
    default:
      return Todo;
  }
};

export const Content: FC<{ entry: Entry }> = ({ entry }) => {
  const Component = getContentComponent(entry.type);

  return (
    <Drawer.Content>
      <Component entry={entry} />
    </Drawer.Content>
  );
};

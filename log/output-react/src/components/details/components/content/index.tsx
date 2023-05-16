import { FC } from 'react';
import { Drawer } from '@robocorp/components';

import { Entry, Type } from '~/lib/types';

import { Log, Variable, Suite } from './components';

type Props = {
  entry: Entry;
};

const getContentComponent = (type: Type) => {
  switch (type) {
    case Type.variable:
      return Variable;
    case Type.log:
      return Log;
    default:
      return Log;
  }
};

export const Content: FC<Props> = ({ entry }) => {
  const Component = getContentComponent(entry.type);

  return (
    <Drawer.Content>
      <Component entry={entry} />
    </Drawer.Content>
  );
};

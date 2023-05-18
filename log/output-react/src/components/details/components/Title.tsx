import { Drawer } from '@robocorp/components';
import { FC } from 'react';

import { Entry, EntryMethod, Type } from '~/lib/types';

type Props = {
  entry: Entry;
};

const getTitle = (entry: Entry) => {
  switch (entry.type) {
    case Type.method:
      const methodEntry = entry as EntryMethod;
      return {
        title: methodEntry.name,
        description: `Module: ${methodEntry.libname}`,
      };

    default:
      return {
        title: 'TODO: Provide title for ' + entry.type,
        description: 'TODO: Provide description for ' + entry.type,
      };
  }
};

export const Title: FC<Props> = ({ entry }) => {
  const { title, description } = getTitle(entry);

  return (
    <Drawer.Header>
      <Drawer.Header.Title title={title} />
      <Drawer.Header.Description>{description}</Drawer.Header.Description>
    </Drawer.Header>
  );
};

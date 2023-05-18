import { Box, Drawer } from '@robocorp/components';
import { styled } from '@robocorp/theme';
import { FC } from 'react';

import {
  Entry,
  EntryException,
  EntryMethod,
  EntryTask,
  EntryVariable,
  Type,
} from '../../../lib/types';

const PreBox = styled(Box)`
  white-space: pre-wrap;
  word-break: break-word;
  display: inline;
`;

type Props = {
  entry: Entry;
};

const getTitle = (entry: Entry) => {
  switch (entry.type) {
    case Type.method:
      const methodEntry = entry as EntryMethod;
      return {
        title: `Method: ${methodEntry.name}`,
        description: `Module: ${methodEntry.libname}`,
      };
    case Type.exception:
      const excEntry = entry as EntryException;
      return {
        title: `Exception: ${excEntry.excType}`,
        description: <PreBox>{excEntry.excMsg.trim()}</PreBox>,
      };
    case Type.variable:
      const excVar = entry as EntryVariable;
      return {
        title: `Variable: ${excVar.name}`,
        description: <PreBox>Type: {excVar.varType.trim()}</PreBox>,
      };
    case Type.task:
      const excTask = entry as EntryTask;
      return {
        title: `Task: ${excTask.name}`,
        description: <PreBox>(task entry point)</PreBox>,
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

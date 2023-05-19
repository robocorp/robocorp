import { Box, Drawer } from '@robocorp/components';
import { styled } from '@robocorp/theme';
import { FC } from 'react';

import {
  Entry,
  EntryException,
  EntryGenerator,
  EntryMethod,
  EntryMethodBase,
  EntryResumeYieldFrom,
  EntryTask,
  EntryUntrackedGenerator,
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
  let prefix = undefined;
  switch (entry.type) {
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
    case Type.method:
      prefix = prefix || 'Method';
    case Type.generator:
      prefix = prefix || 'Enter generator';
    case Type.untrackedGenerator:
      prefix = prefix || 'Enter a generator in library (lifecycle not tracked)';
    case Type.resumeYield:
      prefix = prefix || 'Resume generator with "yield"';
    case Type.resumeYieldFrom:
      prefix = prefix || 'Resume generator with "yield from"';
    case Type.suspendYield:
      prefix = prefix || 'Suspend generator with "yield"';
    case Type.suspendYieldFrom:
      prefix = prefix || 'Suspend generator with "yield from"';
      const methodEntry = entry as EntryMethodBase;
      return {
        title: `${prefix}: ${methodEntry.name}`,
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

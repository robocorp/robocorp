import { FC, ReactNode } from 'react';
import { Box, Typography } from '@robocorp/components';
import { styled } from '@robocorp/theme';

import {
  Entry,
  EntryConsole,
  EntryException,
  EntryGenerator,
  EntryLog,
  EntryMethodBase,
  EntryReturn,
  EntrySuspendYield,
  EntryThreadDump,
  EntryUntrackedGenerator,
  EntryVariable,
  Type,
} from '~/lib/types';
import {
  IMG_HEIGHT_SMALL,
  IMG_MARGIN_SMALL,
  extractDataFromImg,
  formatArguments,
  replaceNewLineChars,
  sanitizeHTML,
} from '~/lib/helpers';

type Props = {
  entry: Entry;
};

const Container = styled(Box)`
  flex: 1;
  min-width: 0px;
  height: auto;

  > pre {
    max-height: ${({ theme }) => theme.space.$48};
  }
`;

export const getValue = (entry: Entry): ReactNode | string => {
  switch (entry.type) {
    case Type.method:
    case Type.generator:
    case Type.untrackedGenerator:
    case Type.resumeYield:
    case Type.resumeYieldFrom:
    case Type.ifElement:
    case Type.elseElement:
      return formatArguments(entry as EntryMethodBase | EntryGenerator | EntryUntrackedGenerator);
    case Type.task:
      return '';
    case Type.suspendYieldFrom:
      return '';
    case Type.processSnapshot:
      return '';
    case Type.exception:
      return (entry as EntryException).excMsg; // We resize this one (so, don't remove new lines)
    case Type.threadDump:
      return replaceNewLineChars((entry as EntryThreadDump).threadDetails);
    case Type.log:
      const entryLog = entry as EntryLog;
      if (entryLog.isHtml) {
        // Special handling for img.
        const initialHTML = entryLog.message;
        let handledHTML = initialHTML.trim();
        const dataSrc = extractDataFromImg(handledHTML);
        if (dataSrc !== undefined) {
          // Ok, we're dealing with an image.
          return (
            <img src={dataSrc} height={IMG_HEIGHT_SMALL} style={{ margin: IMG_MARGIN_SMALL }} />
          );
        }

        // Could not recognize as image. Handle as "random" html.
        const sanitizedHTML = sanitizeHTML(handledHTML);
        return <div dangerouslySetInnerHTML={{ __html: sanitizedHTML }}></div>;
      } else {
        return entryLog.message; // We resize this one (so, don't remove new lines)
      }
    case Type.console:
      const entryConsole = entry as EntryConsole;
      return entryConsole.message; // We resize this one (so, don't remove new lines)
    case Type.variable:
      const entryVariable = entry as EntryVariable;
      return replaceNewLineChars(`${entryVariable.value} (${entryVariable.varType})`);
    case Type.returnElement:
      const entryReturn = entry as EntryReturn;
      return replaceNewLineChars(`${entryReturn.value} (${entryReturn.varType})`);
    case Type.suspendYield:
      const entrySuspendYield = entry as EntrySuspendYield;
      return replaceNewLineChars(
        `Yielded: ${entrySuspendYield.value} (${entrySuspendYield.varType})`,
      );
    default:
      return 'TODO: provide getValue for: ' + entry.type;
  }
};

export const StepValue: FC<Props> = ({ entry }) => {
  const value = getValue(entry);
  const isString = typeof value === 'string';
  return (
    <Container flex="1" className="entryValue">
      {isString ? (
        <Typography
          mr="$8"
          mt={6}
          as="pre"
          fontFamily="code"
          variant="body.small"
          color="content.subtle.light"
          fontWeight="bold"
          truncate={1}
        >
          {value}
        </Typography>
      ) : (
        value
      )}
    </Container>
  );
};

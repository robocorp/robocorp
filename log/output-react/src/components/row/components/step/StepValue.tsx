import { FC, ReactNode, useCallback, MouseEvent, useMemo } from 'react';
import { Box, Typography } from '@robocorp/components';
import { styled } from '@robocorp/theme';
import './step.css';

import {
  Entry,
  EntryAssertFailed,
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
  truncateString,
} from '~/lib/helpers';
import { useLogContext } from '~/lib';

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
    case Type.assertFailed:
      return formatArguments(
        entry as EntryMethodBase | EntryGenerator | EntryUntrackedGenerator | EntryAssertFailed,
      );
    case Type.continueElement:
    case Type.breakElement:
    case Type.task:
    case Type.suspendYieldFrom:
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
  const value = useMemo(() => {
    const ret = getValue(entry);
    if (!ret) {
      return ret;
    }
    if (typeof ret === 'string') {
      // In Firefox providing a big string makes the layout engine
      // work very slowly (not really an issue on Chrome).
      return truncateString(ret, 300);
    }
    return ret;
  }, [entry]);

  const isString = typeof value === 'string';
  const { setDetailsIndex } = useLogContext();

  const onClickShowDetails = useCallback(
    (e: MouseEvent) => {
      e.stopPropagation();
      setDetailsIndex({ indexAll: entry.entryIndexAll });
    },
    [entry],
  );

  // We use the dontStretchContents to set display: inline-block;
  // if we don't do that, the value contents will stretch through
  // much more than intended and it can be hard for the user to
  // click a row in the list for selecting it (as most of it will
  // be the target to open the details).
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
          onClick={onClickShowDetails}
          style={{ cursor: 'pointer' }}
          className="dontStretchContents"
        >
          {value}
        </Typography>
      ) : (
        <Box
          onClick={onClickShowDetails}
          className="dontStretchContents"
          style={{ cursor: 'pointer' }}
        >
          {value}
        </Box>
      )}
    </Container>
  );
};

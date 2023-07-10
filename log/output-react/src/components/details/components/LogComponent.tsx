import { FC } from 'react';
import { extractDataFromImg, sanitizeHTML } from '~/lib';

import { Entry, EntryConsole, EntryLog, Type } from '~/lib/types';
import { PreBox, SourceAndLine } from './Common';
import { Header } from '@robocorp/components';

export const LogComponent: FC<{ entry: Entry }> = (props) => {
  let message = '';
  if (props.entry.type == Type.log) {
    const entryLog = props.entry as EntryLog;
    if (entryLog.isHtml) {
      // Special handling for img.
      const initialHTML = entryLog.message;
      let handledHTML = initialHTML.trim();
      const dataSrc = extractDataFromImg(handledHTML);
      if (dataSrc !== undefined) {
        // Ok, we're dealing with an image.
        return <img src={dataSrc} height={'100%'} width={'100%'} />;
      }

      // Could not recognize as image. Handle as "random" html.
      const sanitizedHTML = sanitizeHTML(handledHTML);
      return <div dangerouslySetInnerHTML={{ __html: sanitizedHTML }}></div>;
    }

    message = entryLog.message;
    return (
      <>
        <PreBox>{message}</PreBox>
        <SourceAndLine source={entryLog.source} lineno={entryLog.lineno}></SourceAndLine>
      </>
    );
  } else if (props.entry.type == Type.console) {
    const entryConsole = props.entry as EntryConsole;
    message = entryConsole.message;
    return <PreBox>{message}</PreBox>;
  }
  return <></>;
};

import { FC } from 'react';
import { extractDataFromImg, sanitizeHTML } from '~/lib';

import { Entry, EntryLog } from '~/lib/types';
import { PreBox } from './Common';

export const LogComponent: FC<{ entry: Entry }> = (props) => {
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
  return <PreBox>{entryLog.message}</PreBox>;
};

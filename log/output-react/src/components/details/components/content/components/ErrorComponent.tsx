import { FC } from 'react';

import { Entry, EntryException } from '~/lib/types';

export const ErrorComponent: FC<{ entry: Entry }> = (props) => {
  const entryMethod: EntryException = props.entry as EntryException;

  return <>Log content</>;
};

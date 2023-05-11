import { Entry, Type } from './types';

const searchFn = (haystack: string, needle: string) =>
  haystack.toLowerCase().includes(needle.trim().toLowerCase());

export const addEntries = (currentEntries: Entry[], newEntries: Partial<Entry>[]) => {
  // TODO: Actual transformation from the log event to Entry has to be done
  const transformedEntries = newEntries.map(
    (entry, index) =>
      ({
        ...entry,
        id: `${currentEntries.length + index}`,
      } as Entry),
  );

  return currentEntries.concat(transformedEntries);
};

// TODO: Update search logic
export const filterEntries = (data: Entry[], filter: string, expandedItems: string[]): Entry[] => {
  return data.filter((entry) => {
    if (entry.id.indexOf('-') > 0 && filter.length === 0) {
      const parentId = entry.id.split('-').slice(0, -1).join('-');
      return expandedItems.includes(parentId);
    }

    if (filter.length === 0) {
      return true;
    }

    if (entry.type === Type.suite) {
      return searchFn(entry.name, filter);
    }

    if (entry.type === Type.variable) {
      return searchFn(entry.name, filter);
    }

    return false;
  });
};

// TODO: Update location format
export const formatLocation = (entry: Entry) => {
  return `${entry.source}:${entry.lineNo}`;
};

// TODO: Update duration format
export const formatDuration = (duration: number) => {
  return `${duration}s`;
};

// TODO: Update item heights to cover all special cases
export const getLogEntryHeight = (entry: Entry): number => {
  if (entry.type === Type.error) {
    // Error entry height is dependent of the message line count
    return 32 + Math.min((entry.message.split(/\r\n|\r|\n/).length - 1) * 16, 32);
  }

  return 32;
};

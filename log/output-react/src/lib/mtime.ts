import { Counter } from './helpers';

const globalCounter = new Counter(1);

export const getNextMtime = (): number => {
  return globalCounter.next();
};

export type MTimeKind = 'invalidateTree' | 'searchApplied' | 'scroll' | 'focus' | 'test';

const handled: Map<MTimeKind, number> = new Map();

const setHandledMtime = (kind: MTimeKind, mtime: number): void => {
  handled.set(kind, mtime);
};

export const wasMtimeHandled = (kind: MTimeKind, mtime: number): boolean => {
  if (mtime === -1) {
    // Nothing was actually set for now.
    return true;
  }

  const foundMtime = handled.get(kind);
  if (foundMtime === undefined) {
    return false;
  }
  return foundMtime >= mtime;
};

/**
 * If the mtime was actually updated returns true (this means that
 * some action should be executed because the new mtime > existing mtime).
 * Otherwise returns false (which means that this mtime was already executed).
 */
export const updateMtime = (kind: MTimeKind, mtime: number): boolean => {
  if (!wasMtimeHandled(kind, mtime)) {
    setHandledMtime(kind, mtime);
    return true;
  }
  return false;
};

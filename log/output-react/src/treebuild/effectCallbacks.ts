import { RunInfo } from '~/lib';
import { Entry } from '~/lib/types';

let callsToSetAllEntries: { newEntries: Entry[]; updatedFromIndex: number } | undefined;
let reactSetAllEntriesCallback: any;

/**
 * To be called from react to set the callback to be used to set the entries (should be called inside of useEffect()).
 */
export function reactCallSetAllEntriesCallback(setAllentriesCallback: any) {
  reactSetAllEntriesCallback = setAllentriesCallback;
  if (callsToSetAllEntries !== undefined) {
    setAllentriesCallback(callsToSetAllEntries.newEntries, callsToSetAllEntries.updatedFromIndex);
    callsToSetAllEntries = undefined;
  }
}

/**
 * Sets the entries. May be done right now if the react callback is already set or it may be
 * done at a later time (when the callback is actually set).
 */
export function setAllEntriesWhenPossible(newEntries: Entry[], updatedFromIndex = 0) {
  if (reactSetAllEntriesCallback !== undefined) {
    reactSetAllEntriesCallback(newEntries, updatedFromIndex);
  } else {
    if (callsToSetAllEntries !== undefined) {
      updatedFromIndex = Math.min(updatedFromIndex, callsToSetAllEntries.updatedFromIndex);
    }
    callsToSetAllEntries = { newEntries, updatedFromIndex };
  }
}

let callsToSetRunInfo: { runInfo: RunInfo } | undefined;
let reactSetRunInfoCallback: any;

export function reactCallSetRunInfoCallback(setRunInfoCallback: any) {
  reactSetRunInfoCallback = setRunInfoCallback;
  if (callsToSetRunInfo !== undefined) {
    setRunInfoCallback(callsToSetRunInfo.runInfo);
    callsToSetRunInfo = undefined;
  }
}

export function setRunInfoWhenPossible(runInfo: RunInfo) {
  if (reactSetRunInfoCallback !== undefined) {
    reactSetRunInfoCallback(runInfo);
  } else {
    callsToSetRunInfo = { runInfo };
  }
}

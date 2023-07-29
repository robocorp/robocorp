import { RunIdsAndLabel, RunInfo } from '~/lib';
import { Entry } from '~/lib/types';

let callsToSetAllEntries:
  | {
      allEntries: Entry[];
      idToEntry: Map<string, Entry>;
      newExpanded: string[];
      updatedFromIndex: number;
    }
  | undefined;
let reactSetAllEntriesCallback: any;

/**
 * To be called from react to set the callback to be used to set the entries (should be called inside of useEffect()).
 */
export function reactCallSetAllEntriesCallback(setAllentriesCallback: any) {
  reactSetAllEntriesCallback = setAllentriesCallback;
  if (callsToSetAllEntries !== undefined) {
    setAllentriesCallback(
      callsToSetAllEntries.allEntries,
      callsToSetAllEntries.idToEntry,
      callsToSetAllEntries.newExpanded,
      callsToSetAllEntries.updatedFromIndex,
    );
    callsToSetAllEntries = undefined;
  }
}

/**
 * Sets the entries. May be done right now if the react callback is already set or it may be
 * done at a later time (when the callback is actually set).
 */
export function setAllEntriesWhenPossible(
  allEntries: Entry[], // all the entries which should be set
  idToEntry: Map<string, Entry>, // a map of entry id -> entry
  newExpanded: string[], // new entry ids to be expanded
  updatedFromIndex = -1, // from which index onwards was there some change
) {
  if (reactSetAllEntriesCallback !== undefined) {
    reactSetAllEntriesCallback(allEntries, idToEntry, newExpanded, updatedFromIndex);
  } else {
    if (callsToSetAllEntries !== undefined) {
      if (updatedFromIndex === -1) {
        updatedFromIndex = callsToSetAllEntries.updatedFromIndex;
      } else if (callsToSetAllEntries.updatedFromIndex === -1) {
        updatedFromIndex = callsToSetAllEntries.updatedFromIndex;
      } else {
        updatedFromIndex = Math.min(updatedFromIndex, callsToSetAllEntries.updatedFromIndex);
      }
      newExpanded = callsToSetAllEntries.newExpanded.concat(newExpanded);
    }
    callsToSetAllEntries = { allEntries, idToEntry, newExpanded, updatedFromIndex };
  }
}

// Set the run info (react bridge).

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

// Set the ids and labels in the select (react bridge).

let callsToSetRunIdsAndLabel: { runIdsAndLabel: RunIdsAndLabel } | undefined;
let reactSetRunIdsAndLabelCallback: any;

export function reactCallSetRunIdsAndLabelCallback(setRunIdsAndLabelCallback: any) {
  reactSetRunIdsAndLabelCallback = setRunIdsAndLabelCallback;
  if (callsToSetRunIdsAndLabel !== undefined) {
    setRunIdsAndLabelCallback(callsToSetRunIdsAndLabel.runIdsAndLabel);
    callsToSetRunIdsAndLabel = undefined;
  }
}

export function setRunIdsAndLabelWhenPossible(runIdsAndLabel: RunIdsAndLabel) {
  if (reactSetRunIdsAndLabelCallback !== undefined) {
    reactSetRunIdsAndLabelCallback(runIdsAndLabel);
  } else {
    callsToSetRunIdsAndLabel = { runIdsAndLabel };
  }
}

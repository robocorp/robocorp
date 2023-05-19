import { StatusLevel } from '../lib/types';

export function getIntLevelFromStatus(status: string): StatusLevel {
  switch (status) {
    case 'FAIL':
    case 'ERROR':
      return StatusLevel.error;
    case 'WARN':
      return StatusLevel.warn;
    case 'NOT RUN':
    case 'NOT_RUN':
      return StatusLevel.unset;
    case 'PASS':
      return StatusLevel.success;
    default:
      console.log(`Unexpected status: ${status}`);
      console.trace();
      return StatusLevel.unset;
  }
}

export function getIntLevelFromStatus(status: string): number {
  switch (status) {
    case 'FAIL':
    case 'ERROR':
      return 2;
    case 'WARN':
      return 1;
    case 'NOT RUN':
    case 'NOT_RUN':
      return -1;
    case 'PASS':
      return 0;
    default:
      return 0;
  }
}

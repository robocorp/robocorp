import { getNextMtime, updateMtime, wasMtimeHandled } from '../lib/mtime';

test('Mtime API.', async () => {
  expect(wasMtimeHandled('test', -1)).toBe(true);

  const mtime = getNextMtime();
  expect(mtime).toBeGreaterThan(0);

  expect(wasMtimeHandled('test', mtime)).toBe(false);
  expect(updateMtime('test', mtime)).toBe(true);
  expect(wasMtimeHandled('test', mtime)).toBe(true);
  expect(wasMtimeHandled('test', -1)).toBe(true);
});

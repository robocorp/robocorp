import { formatTimeInSeconds } from '../lib/helpers';

test('Time print.', () => {
  expect(formatTimeInSeconds(10)).toBe('10.0 s');
  expect(formatTimeInSeconds(32.11)).toBe('32.1 s');
  expect(formatTimeInSeconds(60)).toBe('01:00 min');
  expect(formatTimeInSeconds(90.1)).toBe('01:30 min');
  expect(formatTimeInSeconds(3600)).toBe('1:00 hours');
  expect(formatTimeInSeconds(3670)).toBe('1:01 hours');
});

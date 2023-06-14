import { prettyPrint } from '../lib/prettyPrint';

test('Format variables.', () => {
  let indent = '    ';
  expect(prettyPrint('{"name": "John", "age": 30}')).toBe(
    `{\n${indent}"name": "John",\n${indent}"age": 30\n}`,
  );

  // Not ideal (we could remove the last \n${indent})
  expect(prettyPrint('{"name": "John", "age": 30,}')).toBe(
    `{\n${indent}"name": "John",\n${indent}"age": 30,\n${indent}\n}`,
  );

  // Unclosed
  expect(prettyPrint('{"name": "John')).toBe(`{\n${indent}"name": "John`);

  // Decode \r\n from string reprs.
  expect(prettyPrint('"Some\\nmulti\\nline\\n"')).toBe(`"""Some\nmulti\nline\n"""`);
});

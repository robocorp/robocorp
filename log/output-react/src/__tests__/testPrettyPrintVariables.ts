import { OPTS, prettyPrint } from '../lib/prettyPrint';

test('Format variables.', () => {
  const original = OPTS.SMALL_LINE;
  try {
    OPTS.SMALL_LINE = 0;

    let indent = '    ';
    expect(prettyPrint('{"name": "John", "age": 30}')).toBe(
      `{\n${indent}"name": "John",\n${indent}"age": 30\n}`,
    );

    // Not ideal (we could remove the last \n${indent})
    expect(prettyPrint('{"name": "John", "age": 30,}')).toBe(
      `{\n${indent}"name": "John",\n${indent}"age": 30,\n${indent}\n}`,
    );

    // Unclosed
    expect(prettyPrint('{"name": "John')).toBe(`{"name": "John`);

    // Decode \r\n from string reprs.
    expect(prettyPrint('"Some\\nmulti\\nline\\n"')).toBe(`"""Some\nmulti\nline\n"""`);

    OPTS.SMALL_LINE = 13;
    expect(prettyPrint('[1,2,3]')).toBe(`[1, 2, 3]`);
    expect(prettyPrint('[1,2,3,4,5,6,7,8,9,10]')).toBe(
      `[\n${indent}1,\n${indent}2,\n${indent}3,\n${indent}4,\n${indent}5,\n${indent}6,\n${indent}7,\n${indent}8,\n${indent}9,\n${indent}10\n]`,
    );
    expect(prettyPrint("(['a', 'b'],)")).toBe("(['a', 'b'], )");
  } finally {
    OPTS.SMALL_LINE = original;
  }
});

test('Format variables bad.', () => {
  expect(prettyPrint('"unclosed str')).toBe(`"unclosed str`);
  expect(prettyPrint('["unclosed str')).toBe(`["unclosed str`);
  expect(prettyPrint('] ) } unmatched')).toBe(`] ) } unmatched`);
});

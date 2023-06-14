function findNextSingle(i: number, curr: string, full: string): number {
  let ignoreNext = false;

  const len = full.length;
  while (i < len) {
    const c = full[i];

    if (!ignoreNext && c === curr) {
      return i;
    }

    if (!ignoreNext) {
      if (c === '\\') {
        // escaped quote, ignore the next char even if it is a ' or "
        ignoreNext = true;
      }
    } else {
      ignoreNext = false;
    }

    i++;
  }

  return i;
}

function formatStr(s: string): string {
  const newS = s.replaceAll('\\n', '\n');
  if (newS.length === s.length) {
    return s;
  }
  const c = s.charAt(0);
  if (s.charAt(s.length - 1) == c) {
    return `${c}${c}${newS}${c}${c}`;
  } else {
    return `${c}${c}${newS}`;
  }
}

/**
 * Formats a string value from the logging and shows it prettier
 * (adding new lines/indentation as needed)
 */
export function prettyPrint(full: string) {
  let indentationLevel: number = 0;
  let indentationString: string = '';
  const formatted: string[] = [];

  function updateIndentationString() {
    indentationString = '    '.repeat(indentationLevel);
  }

  const len = full.length;
  let skipSpaces = false;
  for (let i = 0; i < len; i++) {
    const currentChar = full[i];

    if (currentChar === '"' || currentChar === "'") {
      const j = findNextSingle(i + 1, currentChar, full);
      formatted.push(formatStr(full.substring(i, j + 1)));
      i = j;
      continue;
    }

    if (skipSpaces && (currentChar == ' ' || currentChar == '\t')) {
      continue;
    }
    skipSpaces = false;

    if (currentChar === '{' || currentChar === '[' || currentChar === '(') {
      // Add indentation after opening a bracket.
      indentationLevel++;
      updateIndentationString();
      formatted.push(currentChar, '\n', indentationString);
    } else if (currentChar === '}' || currentChar === ']' || currentChar === ')') {
      // Decrease the indentation level after closing a bracket.
      indentationLevel--;
      updateIndentationString();
      formatted.push('\n', indentationString, currentChar);
    } else if (currentChar === ',') {
      // Add a new line after comma
      formatted.push(currentChar, '\n', indentationString);
      skipSpaces = true;
    } else {
      formatted.push(currentChar);
    }
  }

  const ret = formatted.join('');
  // console.log(ret);
  return ret;
}

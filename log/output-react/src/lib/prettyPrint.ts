import { logError } from './helpers';
import { ParsingUtils } from './parsingUtils';

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

export const OPTS = {
  SMALL_LINE: 40,
};

class PrettyPrinter {
  indentationLevel: number;
  indentationString: string;
  formatted: string[];
  parsing: ParsingUtils;
  len: number;
  skipSpaces: boolean;
  full: string;

  constructor(full: string) {
    this.indentationLevel = 0;
    this.indentationString = '';
    this.formatted = [];
    this.full = full;

    this.updateIndentationString();

    this.parsing = new ParsingUtils(full, true);

    this.len = full.length;
    this.skipSpaces = false;
  }

  updateIndentationString() {
    this.indentationString = '    '.repeat(this.indentationLevel);
  }

  formatInSingleLine(start: number, end: number) {
    for (let i = start; i < end; i++) {
      const currentChar = this.parsing.charAt(i);

      if (currentChar === '"' || currentChar === "'") {
        let j = this.parsing.findNextSingle(i + 1, currentChar);
        if (j == -1) {
          j = this.len;
        }
        this.formatted.push(formatStr(this.full.substring(i, j + 1)));
        i = j;
        continue;
      }

      if (this.skipSpaces && (currentChar == ' ' || currentChar == '\t')) {
        continue;
      }
      this.skipSpaces = false;

      if (currentChar == ',') {
        this.formatted.push(currentChar, ' ');
        this.skipSpaces = true;
        continue;
      }
      this.formatted.push(currentChar);
    }
  }

  formatStr() {
    for (let i = 0; i < this.len; i++) {
      const currentChar = this.parsing.charAt(i);

      if (currentChar === '"' || currentChar === "'") {
        let j = this.parsing.findNextSingle(i + 1, currentChar);
        if (j == -1) {
          j = this.len;
        }
        this.formatted.push(formatStr(this.full.substring(i, j + 1)));
        i = j;
        continue;
      }

      if (this.skipSpaces && (currentChar == ' ' || currentChar == '\t')) {
        continue;
      }
      this.skipSpaces = false;

      if (currentChar === '{' || currentChar === '[' || currentChar === '(') {
        const j = this.parsing.eatPar(i, null, currentChar);
        if (j == -1) {
          this.formatted.push(currentChar);
          continue;
        }

        if (j - i < OPTS.SMALL_LINE) {
          this.formatInSingleLine(i, j + 1);
          i = j;
        } else {
          // Add indentation after opening a bracket.
          this.indentationLevel++;
          this.updateIndentationString();
          this.formatted.push(currentChar, '\n', this.indentationString);
        }
      } else if (currentChar === '}' || currentChar === ']' || currentChar === ')') {
        // Decrease the indentation level after closing a bracket.
        if (this.indentationLevel > 0) {
          this.indentationLevel--;
          this.updateIndentationString();
          this.formatted.push('\n', this.indentationString, currentChar);
        } else {
          this.formatted.push(currentChar);
        }
      } else if (currentChar === ',') {
        // Add a new line after comma
        this.formatted.push(currentChar, '\n', this.indentationString);
        this.skipSpaces = true;
      } else {
        this.formatted.push(currentChar);
      }
    }
    return this.formatted.join('');
  }
}

export function prettyPrint(full: string) {
  try {
    const printer = new PrettyPrinter(full);
    const ret = printer.formatStr();
    // console.log(ret);
    return ret;
  } catch (err) {
    // Something bad happened: show original.
    console.log('Error pretty-printing: ' + full);
    logError(err);
    return full;
  }
}

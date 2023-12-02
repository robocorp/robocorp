function getPeer(c: string) {
    switch (c) {
      case '{':
        return '}';
      case '}':
        return '{';
      case '(':
        return ')';
      case ')':
        return '(';
      case '[':
        return ']';
      case ']':
        return '[';
      case '>':
        return '<';
      case '<':
        return '>';
      case "'":
        return "'";
      case '"':
        return '"';
      case '/':
        return '/';
      case '`':
        return '`';
    }
  
    throw new Error('Unable to find peer for :' + c);
  }
  
  class SyntaxErrorException extends Error {
    constructor() {
      super('Unclosed peers found.');
      this.name = 'SyntaxErrorException';
    }
  }
  
  export class FastStringBuffer {
    rightTrimWhitespacesAndTabs() {
      while (true) {
        if (this.contents.length === 0) {
          return;
        }
        const c = this.contents.at(-1);
        if (c === ' ' || c == '\t') {
          this.contents.pop();
        } else {
          break;
        }
      }
    }
    contents: string[] = [];
    append(c: string) {
      this.contents.push(c);
    }
  }
  
  export class ParsingUtils {
    contents: string;
    returnNegativeOnNoMatch: boolean;
  
    constructor(contents: string, returnNegativeOnNoMatch: boolean) {
      this.returnNegativeOnNoMatch = returnNegativeOnNoMatch;
      this.contents = contents;
    }
  
    len() {
      return this.contents.length;
    }
  
    charAt(i: number): string {
      return <string>this.contents.at(i);
    }
  
    eatComments(buf: FastStringBuffer | null, i: number): number {
      return this.eatComments2(buf, i, true);
    }
  
    eatComments2(buf: FastStringBuffer | null, i: number, addNewLine: boolean): number {
      const len = this.len();
      let c = '\0';
  
      while (i < len && (c = this.charAt(i)) !== '\n' && c !== '\r') {
        if (buf !== null) {
          buf.append(c);
        }
        i++;
      }
  
      if (!addNewLine) {
        if (c === '\r' || c === '\n') {
          i--;
          return i;
        }
      }
  
      if (i < len) {
        if (buf !== null) {
          buf.append(c);
        }
        if (c === '\r') {
          if (i + 1 < len && this.charAt(i + 1) === '\n') {
            i++;
            if (buf !== null) {
              buf.append('\n');
            }
          }
        }
      }
  
      return i;
    }
  
    eatWhitespaces(buf: FastStringBuffer | null, i: number): number {
      const len = this.len();
  
      while (i < len && this.charAt(i) === ' ') {
        if (buf !== null) {
          buf.append(this.charAt(i));
        }
        i++;
      }
  
      i--;
  
      return i;
    }
  
    eatLiterals(buf: FastStringBuffer | null, startPos: number): number {
      return this.eatLiterals2(buf, startPos, false);
    }
  
    eatLiterals2(
      buf: FastStringBuffer | null,
      startPos: number,
      rightTrimMultiline: boolean,
    ): number {
      const startChar = this.charAt(startPos);
  
      if (startChar !== '"' && startChar !== "'") {
        throw new Error(`Wrong location to eat literals. Expecting ' or ". Found: >>${startChar}<<`);
      }
  
      const endPos = this.getLiteralEnd(startPos, startChar);
  
      if (buf !== null) {
        const rightTrim = rightTrimMultiline && this.isMultiLiteral(startPos, startChar);
        const lastPos = Math.min(endPos, this.len() - 1);
        for (let i = startPos; i <= lastPos; i++) {
          const ch = this.charAt(i);
          if (rightTrim && (ch === '\r' || ch === '\n')) {
            buf.rightTrimWhitespacesAndTabs();
          }
          buf.append(ch);
        }
      }
      return endPos;
    }
  
    /**
     * @param i current position (should have a ' or ")
     * @param curr the current char (' or ")
     * @return whether we are at the start of a multi line literal or not.
     */
    isMultiLiteral(i: number, curr: string) {
      const len: number = this.len();
      if (len <= i + 2) {
        return false;
      }
      if (this.charAt(i + 1) == curr && this.charAt(i + 2) == curr) {
        return true;
      }
      return false;
    }
  
    getLiteralEnd(i: number, curr: string): number {
      const multi = this.isMultiLiteral(i, curr);
  
      let j: number;
      if (multi) {
        j = this.findNextMulti(i + 3, curr);
      } else {
        j = this.findNextSingle(i + 1, curr);
      }
      return j;
    }
  
    eatPar(i: number, buf: FastStringBuffer | null, par: string): number {
      let c = ' ';
  
      const closingPar = getPeer(par);
  
      let j = i + 1;
      const len = this.len();
      while (j < len && (c = this.charAt(j)) !== closingPar) {
        j++;
  
        if (c === "'" || c === '"') {
          j = this.eatLiterals(null, j - 1) + 1;
          if (j == 0 && this.returnNegativeOnNoMatch) {
            return -1;
          }
        } else if (c === par) {
          j = this.eatPar(j - 1, null, par) + 1;
          if (j == 0 && this.returnNegativeOnNoMatch) {
            return -1;
          }
        } else {
          if (buf !== null) {
            buf.append(c);
          }
        }
      }
      if (this.returnNegativeOnNoMatch && c !== closingPar) {
        return -1;
      }
      if (j >= len) {
        j = len;
      }
      return j;
    }
  
    findNextSingle(i: number, curr: string): number {
      let ignoreNext = false;
      const len = this.len();
      while (i < len) {
        const c = this.charAt(i);
  
        if (!ignoreNext && c === curr) {
          return i;
        }
  
        if (!ignoreNext) {
          if (c === '\\') {
            ignoreNext = true;
          }
        } else {
          ignoreNext = false;
        }
  
        i++;
      }
      if (this.returnNegativeOnNoMatch) {
        return -1;
      }
      return i;
    }
  
    findPreviousSingle(i: number, curr: string): number {
      while (i >= 0) {
        const c = this.charAt(i);
  
        if (c === curr) {
          if (i > 0) {
            if (this.charAt(i - 1) === '\\') {
              i--;
              continue;
            }
          }
          return i;
        }
  
        i--;
      }
      if (this.returnNegativeOnNoMatch) {
        return -1;
      }
      return i;
    }
  
    findNextMulti(i: number, curr: string): number {
      const len = this.len();
      while (i + 2 < len) {
        const c = this.charAt(i);
        if (c === curr && this.charAt(i + 1) === curr && this.charAt(i + 2) === curr) {
          return i + 2;
        }
        i++;
        if (c === '\\') {
          i++;
        }
      }
  
      if (this.returnNegativeOnNoMatch) {
        return -1;
      }
  
      if (len < i + 2) {
        return len;
      }
      return i + 2;
    }
  }
  
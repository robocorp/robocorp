import * as DOMPurify from 'dompurify';
import parseISO from 'date-fns/parseISO';

export function entryIdDepth(id: string) {
  return id.split('-').length - 1;
}

export function truncateString(str: string, maxLength: number): string {
  if (str.length <= maxLength) {
    return str;
  } else {
    return str.substring(0, maxLength - 3) + '...';
  }
}

export const findMinAndMax = (numbers: number[]): [number, number] => {
  if (numbers.length === 0) {
    throw new Error('Array is empty');
  }
  let min = numbers[0];
  let max = numbers[0];

  for (let i = 1; i < numbers.length; i++) {
    if (numbers[i] < min) {
      min = numbers[i];
    }
    if (numbers[i] > max) {
      max = numbers[i];
    }
  }

  return [min, max];
};

export function formatTimeInSeconds(seconds: number) {
  if (seconds < 60) {
    return seconds.toFixed(1) + ' s';
  }

  var hours = Math.floor(seconds / 3600);
  var minutes = Math.floor((seconds % 3600) / 60);
  var remainingSeconds = seconds % 60;

  var formattedTime = '';
  if (hours > 0) {
    formattedTime += hours + ':';
    formattedTime += padZero(minutes) + ' hours';
  } else {
    formattedTime += padZero(minutes) + ':' + padZero(remainingSeconds) + ' min';
  }

  return formattedTime;
}

function padZero(n: number) {
  return n.toFixed(0).padStart(2, '0');
}

export function replaceNewLineChars(text: string) {
  return text.replace(/\n/g, '\\n').replace(/\r/g, '\\r');
}

export function sanitizeHTML(html: string): string {
  let sanitize = DOMPurify.sanitize;
  if (!sanitize) {
    // It can be either in DOMPurify or DOMPurify.default.
    const d = DOMPurify as any;
    sanitize = d.default.sanitize;
  }
  const sanitizedHTML = sanitize(html);
  return sanitizedHTML;
}

export function pathBasenameNoExt(source: string): string {
  let basename = source;
  let index = Math.max(source.lastIndexOf('/'), source.lastIndexOf('\\'));
  if (index > 0) {
    basename = source.substring(index + 1);
  }
  index = basename.lastIndexOf('.');
  if (index > 0) {
    basename = basename.substring(0, index);
  }
  return basename;
}

export function logError(err: any | Error | undefined) {
  if (err !== undefined) {
    let indent = '    ';
    if (err.message) {
      console.log(indent + err.message);
    }
    if (err.stack) {
      let stack: string = '' + err.stack;
      console.log(stack.replace(/^/gm, indent));
    }
  }
}

export class Counter {
  private count: number;

  constructor(initial = 0) {
    this.count = initial;
  }

  public next(): number {
    return this.count++;
  }
}

export const isWindowDefined = () => {
  try {
    let x = window;
  } catch (error) {
    return false;
  }
  return true;
};

export const isDocumentDefined = () => {
  try {
    let x = document;
  } catch (error) {
    return false;
  }
  return true;
};

let parseDate = parseISO;
if (parseDate === undefined) {
  // Note (fabioz): when running npm test the import is returning an undefined,
  // yet a require works (why? no idea...)
  parseDate = require('date-fns/parseISO');
}

export function parseDateisoformatToLocalTimezoneDate(time: string) {
  return parseDate(time);
}

export function parseDateisoformatToLocalTimezoneStr(time: string) {
  const parsedTime = parseDate(time);
  // Note: doing toString() in an utc time (which ends with +00:00)
  // will convert it to the local timezone.
  return parsedTime.toString();
}

export function copyArrayAndInsertElement(array: any[], element: any, position: number): any[] {
  if (position < 0 || position > array.length) {
    throw new Error('Invalid position');
  }

  const newArray = array.slice(0, position); // creates copy

  // add new item in array copy
  newArray.push(element);

  // add remaining items to it
  for (let i = position; i < array.length; i++) {
    newArray.push(array[i]);
  }

  return newArray;
}

export function logError(err: unknown) {
  if (err instanceof Error) {
    const indent = '    ';
    if (err.message) {
      // eslint-disable-next-line no-console
      console.error(indent + err.message);
    }
    if (err.stack) {
      const stack = `${err.stack}`;
      // eslint-disable-next-line no-console
      console.error(stack.replace(/^/gm, indent));
    }
  }
}

export class Counter {
  private count: number;

  constructor(initial = 0) {
    this.count = initial;
  }

  public next(): number {
    this.count += 1;
    return this.count;
  }
}

export function copyArrayAndInsertElement<T>(array: T[], element: T, position: number): T[] {
  if (position < 0 || position > array.length) {
    throw new Error('Invalid position');
  }

  const newArray = array.slice(0, position); // creates copy

  // add new item in array copy
  newArray.push(element);

  // add remaining items to it
  for (let i = position; i < array.length; i += 1) {
    newArray.push(array[i]);
  }

  return newArray;
}

export const prettyPrint = (input: string) => {
  try {
    return JSON.stringify(JSON.parse(input), null, 4);
  } catch {
    return input;
  }
};

export const stringifyResult = (result?: string | boolean | number) => {
  switch (typeof result) {
    case 'string':
      return result;
    case 'number':
      return result.toString();
    case 'boolean':
      return result ? 'true' : 'false';
    default:
      return '';
  }
};

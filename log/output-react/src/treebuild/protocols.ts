export interface ITreeState {
  openNodes: object;
}

type IRunIdToTreeState = {
  [key: string]: ITreeState;
};

export type IFilterLevel = 'ERROR' | 'WARN' | 'PASS';

export interface IState {
  filterLevel: IFilterLevel;
  runIdToTreeState: IRunIdToTreeState;
  runIdLRU: string[];
}

export interface IOpts {
  runId: string | undefined;
  state: IState | undefined;
  onClickReference: Function | undefined;
  allRunIdsToLabel: object | undefined;

  // Contains the initial file contents.
  initialContents: string | undefined;

  // Contains the contents added afterwards (i.e.:
  // we may add the contents for a session up to a point
  // and then add new messages line by line as it's
  // being tracked afterwards).
  appendedContents: string[];
}

export type ConsoleMessagKind =
  | 'regular'
  | 'task_name'
  | 'stdout'
  | 'stderr'
  | 'important'
  | 'error'
  | 'traceback';

export interface IConsoleMessage {
  kind: ConsoleMessagKind;
  message: string;
  time_delta_in_seconds: number;
  source: string;
  lineno: number;
}

export interface ITracebackEntry {
  source: string;
  lineno: number;
  method: string;
  lineContent: string;
  variables: Map<string, string[]>;
}

export class PythonTraceback {
  exceptionMsg: string;

  stack: ITracebackEntry[] = [];

  constructor(exceptionMsg: string) {
    this.exceptionMsg = exceptionMsg;
  }

  pushEntry(source: string, lineno: number, method: string, lineContent: string): void {
    const variables: Map<string, string[]> = new Map();
    this.stack.push({ source, lineno, method, lineContent, variables });
  }

  pushVar(name: string, type: string, value: string): void {
    const st = this.stack.at(-1);
    if (st === undefined) {
      throw new Error('Traceback stack is empty!');
    }
    const { variables } = st;
    variables.set(name, [type, value]);
  }
}

export type ViewSettings = {
  columns: {
    duration: boolean;
    location: boolean;
  };
  theme: 'dark' | 'light';
};

export enum StatusLevel {
  error = 3,
  warn = 2,
  info = 1,
  success = 0,
  unset = -1,
}

export enum Type {
  task = 'Task',
  method = 'Method',

  // Not used for now...
  variable = 'Variable',
  log = 'Log',
  error = 'Error',
}

export interface EntryBase {
  id: string;
  source: string;
  lineno: number;
  type: Type;
  entriesIndex: number;
}

export interface EntryTask extends EntryBase {
  type: Type.task;
  name: string;
  libname: string;
  status: StatusLevel;
  startDeltaInSeconds: number | -1 | undefined;
  endDeltaInSeconds: number | -1 | undefined;
}

export interface EntryMethod extends EntryBase {
  type: Type.method;
  name: string;
  libname: string;
  status: StatusLevel;
  startDeltaInSeconds: number | -1 | undefined;
  endDeltaInSeconds: number | -1 | undefined;
}

export interface EntryVariable extends EntryBase {
  type: Type.variable;
  name: string;
  value: string;
}

export interface EntryLog extends EntryBase {
  type: Type.log;
  status: StatusLevel;
  message: string;
  image?: string;
}

export type Entry = EntryTask | EntryMethod | EntryVariable | EntryLog;

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
  suite = 'Suite',
  task = 'Task',
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

export interface EntrySuite extends EntryBase {
  type: Type.suite;
  date: Date;
  name: string;
}

export interface EntryTask extends EntryBase {
  type: Type.task;
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

export interface EntryError extends EntryBase {
  type: Type.error;
  message: string;
}

export type Entry = EntrySuite | EntryTask | EntryVariable | EntryLog | EntryError;

export interface ActionPackage {
  id: string;
  name: string;
  actions: Action[];
}

export interface Action {
  id: string; // primary key (uuid)
  action_package_id: string; // foreign key to the action package
  name: string; // The action name
  docs: string; // Docs for the action

  // File for the action (relative to the directory in the ActionPackage).
  file: string;
  lineno: number; // Line for the action
  input_schema: string; // The json content for the schema input
  output_schema: string; // The json content for the schema output
}

export interface Run {
  id: string; // primary key (uuid)
  status: number; // 0=not run, 1=running, 2=passed, 3=failed
  action_id: string; // foreign key to the action
  start_time: string; // The time of the run creation.
  run_time?: number | null; // The time from the run creation to the run finish (in seconds)
  inputs: string; // The json content with the variables used as an input
  result?: string | null; // The json content of the output that the run generated
  error_message?: string | null; // If the status=failed, this may have an error message
}

export interface RunTableEntry {
  id: string; // primary key (uuid)
  status: number; // 0=not run, 1=running, 2=passed, 3=failed
  action_id: string; // foreign key to the action
  action_name: string; // foreign key to the action
  start_time: string; // The time of the run creation.
  run_time?: number | null; // The time from the run creation to the run finish (in seconds)
  inputs: string; // The json content with the variables used as an input
  result?: string | null; // The json content of the output that the run generated
  error_message?: string | null; // If the status=failed, this may have an error message
}

export interface LoadedRuns {
  data?: Run[];
  isPending?: boolean;
  errorMessage?: string;
  requestedOnce?: boolean;
}

export interface LoadedActions {
  data?: ActionPackage[];
  isPending?: boolean;
  errorMessage?: string;
  requestedOnce?: boolean;
}

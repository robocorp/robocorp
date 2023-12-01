import { Action, ActionPackage, Run } from './types';

const action1: Action = {
  id: '1',
  action_package_id: 'calc1',
  name: 'Action 1',
  docs: 'Documentation for Action 1',
  file: 'action_1.js',
  lineno: 10,
  input_schema: '{"input1": "string", "input2": "number"}',
  output_schema: '{"output1": "string", "output2": "boolean"}',
};

const action2: Action = {
  id: '2',
  action_package_id: 'calc1',
  name: 'Action 2',
  docs: 'Documentation for Action 2',
  file: 'action_2.js',
  lineno: 15,
  input_schema: '{"input": "string"}',
  output_schema: '{"output": "number"}',
};

const action3: Action = {
  id: '3',
  action_package_id: 'calc1',
  name: 'Action 3',
  docs: 'Documentation for Action 3',
  file: 'action_3.js',
  lineno: 20,
  input_schema: '{"input": "boolean"}',
  output_schema: '{"output": "object"}',
};

export const ACTION_PACKAGE_SAMPLE_DATA: ActionPackage[] = [
  {
    id: 'calc1',
    name: 'calculator',
    actions: [action1, action2, action3],
  },
];

const run1: Run = {
  id: '1',
  status: 2,
  action_id: 'action_1',
  start_time: '2023-11-30T08:00:00Z',
  run_time: 120,
  inputs: '{"input1": "value1", "input2": 42}',
  result: '{"output1": "result1", "output2": 55}',
  error_message: null,
};

const run2: Run = {
  id: '2',
  status: 3,
  action_id: 'action_2',
  start_time: '2023-11-29T15:30:00Z',
  run_time: null,
  inputs: '{"input": "data"}',
  result: null,
  error_message: 'Error occurred during execution.',
};

const run3: Run = {
  id: '3',
  status: 1,
  action_id: 'action_3',
  start_time: '2023-12-01T10:45:00Z',
  run_time: null,
  inputs: '{"param1": true, "param2": 123}',
  result: null,
  error_message: null,
};

export const RUNS = [run1, run2, run3];
for (let index = 4; index < 100; index++) {
  const element = { ...run1 };
  element['id'] = '' + index;
  RUNS.push(element);
}

import { TreeBuilder } from '../treebuild/treeBuilder';
import { createOpts } from '../treebuild/options';
import { EntryBase, EntryMethod, EntryTask, Type } from '../lib/types';

const CREATE_RUN_AND_TEST = `
V 0.0.2
T 2023-04-30T13:35:49.798+00:00
ID 1|eb887eee-e75b-11ed-bdec-202b20a029af
I "sys.platform=win32"
I "python=3.9.16 (main, Mar  8 2023, 10:39:24) [MSC v.1916 64 bit (AMD64)]"
M a:"Robot1"
SR a|0.016
M c:"Simple Task"
M d:"Robot1"
M e:"/path/to/file.py"
M f:""
P b:c|d|e|f|0
ST b|0.016
`;

const START_TEST = `
ST b|0.016
`;
const END_TEST = `
ET g|h|0.017
`;

const FINISH_RUN_AND_TEST = `
M g:"PASS"
M h:"Ok"
ET g|h|0.017
ER g|0.017  
`;

const START_ELEMENT = `
M h:"screenshot"
M i:"robocorp_log_tests._help_screenshot"
M j:"/path/to/_help_screenshot.py"
P g:h|i|j|f|2
M k:"METHOD"
SE g|k|0.012  
`;

const END_ELEMENT = `
M g:"PASS"
M h:"Ok"
M r:"PASS"
EE k|r|0.016
`;

test('TreeBuilder can read task.', async () => {
  const opts = createOpts();
  opts.initialContents = CREATE_RUN_AND_TEST;

  const treeBuilder = new TreeBuilder(opts);

  await treeBuilder.addInitialContents();
  expect(treeBuilder.flattened.entries.length).toBe(1);
  expect(treeBuilder.flattened.stack.length).toBe(1);

  opts.appendedContents.push(FINISH_RUN_AND_TEST);
  await treeBuilder.onAppendedContents();
  expect(treeBuilder.flattened.entries.length).toBe(1);
  expect(treeBuilder.flattened.stack.length).toBe(0);
  const entry: EntryTask = <EntryTask>treeBuilder.flattened.entries[0];
  expect(entry.type === Type.task);
  expect(entry.name === 'Simple Task');
});

test('TreeBuilder can read method.', async () => {
  const opts = createOpts();
  const treeBuilder = new TreeBuilder(opts);

  opts.initialContents = CREATE_RUN_AND_TEST + START_ELEMENT;
  await treeBuilder.addInitialContents();
  expect(treeBuilder.flattened.entries.length).toBe(2);
  expect(treeBuilder.flattened.stack.length).toBe(2);

  opts.appendedContents.push(END_ELEMENT);
  await treeBuilder.onAppendedContents();
  expect(treeBuilder.flattened.entries.length).toBe(2);
  expect(treeBuilder.flattened.stack.length).toBe(1);

  opts.appendedContents.push(START_ELEMENT + END_ELEMENT);
  await treeBuilder.onAppendedContents();
  expect(treeBuilder.flattened.entries.length).toBe(3);
  expect(treeBuilder.flattened.stack.length).toBe(1);

  opts.appendedContents.push(END_TEST);
  await treeBuilder.onAppendedContents();
  expect(treeBuilder.flattened.entries.length).toBe(3);
  expect(treeBuilder.flattened.stack.length).toBe(0);

  const entryTask: EntryTask = <EntryTask>treeBuilder.flattened.entries[0];
  expect(entryTask.type === Type.task);
  expect(entryTask.name === 'Simple Task');
  expect(entryTask.id === 'root0');

  let entryElement: EntryMethod = <EntryMethod>treeBuilder.flattened.entries[1];
  expect(entryElement.type === Type.method);
  expect(entryElement.name === 'screenshot');
  expect(entryTask.id === 'root0-0');

  entryElement = <EntryMethod>treeBuilder.flattened.entries[2];
  expect(entryElement.type === Type.method);
  expect(entryElement.name === 'screenshot');
  expect(entryTask.id === 'root0-1');

  opts.appendedContents.push(START_TEST);
  opts.appendedContents.push(START_ELEMENT);
  opts.appendedContents.push(END_ELEMENT);
  opts.appendedContents.push(FINISH_RUN_AND_TEST);
  await treeBuilder.onAppendedContents();

  let entry = <EntryBase>treeBuilder.flattened.entries[3];
  expect(entry.type === Type.task);
  expect(entry.id === 'root1');

  entry = <EntryBase>treeBuilder.flattened.entries[4];
  expect(entry.type === Type.method);
  expect(entry.id === 'root1-0');

  expect(treeBuilder.flattened.entries.length).toBe(5);
  expect(treeBuilder.flattened.stack.length).toBe(0);
});

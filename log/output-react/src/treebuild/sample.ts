// This function may be changed during development so that a different scenario is loaded.
// The standalone version will replace the contents of the version below to the contents generated
// in the run.
//
// See output-react/README.md for details.
//
// Note: this function shouldn't be changed (when merging to master) as its contents are used as a marker for the
// new contents to be embedded.

export function getSampleContents() {
  const raw = String.raw`V 0.0.2
  T 2023-05-15T14:30:37.751+00:00
  ID 1|0f808d43-f32d-11ed-a9e3-202b20a029af
  I "sys.platform=win32"
  I "python=3.9.16 (main, Mar  8 2023, 10:39:24) [MSC v.1916 64 bit (AMD64)]"
  M a:"Robot1"
  SR a|0.001
  M c:"Simple Task"
  M d:"task_mod"
  M e:"X:/robocorpws/draft-python-framework/log/tests/robocorp_log_tests/test_view_integrated_react.py"
  M f:""
  P b:c|d|e|f|0
  ST b|0.001
  M h:"some_method"
  M i:"robocorp_log_tests._resources.check"
  M j:"X:/robocorpws/draft-python-framework/log/tests/robocorp_log_tests/_resources/check.py"
  P g:h|i|j|f|12
  M k:"METHOD"
  SE g|k|0.001
  M m:"call_another_method"
  P l:m|i|j|f|7
  SE l|k|0.001
  M n:"param0"
  M o:"int"
  M p:"1"
  EA n|o|p
  M q:"param1"
  M r:"str"
  M s:"'arg'"
  EA q|r|s
  M t:"args"
  M u:"tuple"
  M v:"(['a', 'b'],)"
  EA t|u|v
  M w:"kwargs"
  M x:"dict"
  M y:"{'c': 3}"
  EA w|x|y
  M z:"PASS"
  EE k|z|0.001
  EE k|z|0.001
  M A:"Ok"
  ET z|A|0.001
  ER z|0.001
  `;
  const s = JSON.stringify(raw);
  return JSON.parse(s);
}

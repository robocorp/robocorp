// This function may be changed during development so that a different scenario is loaded.
// The standalone version will replace the contents of the version below to the contents generated
// in the run.
//
// See output-webview/README.md for details.
//
// Note: this function shouldn't be changed (when merging to master) as its contents are used as a marker for the
// new contents to be embedded.

export function getSampleContents() {
  let s = JSON.stringify(`V 0.0.2
  T 2023-04-30T13:35:49.798+00:00
  ID 1|eb887eee-e75b-11ed-bdec-202b20a029af
  I "sys.platform=win32"
  I "python=3.9.16 (main, Mar  8 2023, 10:39:24) [MSC v.1916 64 bit (AMD64)]"
  M a:"Robot1"
  SR a|0.016
  M c:"Simple Task"
  M d:"Robot1"
  M e:"X:/robocorpws/robo/log/tests/robocorp_log_tests/test_view_integrated.py"
  M f:""
  P b:c|d|e|f|0
  ST b|0.016
  M g:"PASS"
  M h:"Ok"
  ET g|h|0.017
  ER g|0.017
  `);
  return JSON.parse(s);
}

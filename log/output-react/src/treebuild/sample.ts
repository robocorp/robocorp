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
  T 2023-07-08T11:50:52.961+00:00
  ID 1|b0cfea88-1d85-11ee-bf45-202b20a029af
  I "sys.platform=win32"
  I "python=3.9.16 | packaged by conda-forge | (main, Feb  1 2023, 21:28:38) [MSC v.1929 64 bit (AMD64)]"
  M a:"tasks.py - minimal_task"
  SR a|0.056
  M c:"Collect tasks"
  M d:"setup"
  M e:""
  P b:c|d|e|e|0
  ST b|0.057
  M f:"regular"
  M g:"\nCollecting task minimal_task from: x:\\robocorpws\\vscode-robot-tests\\PythonFmk\\tasks.py\n"
  C f|g|0.057
  M h:"PASS"
  ET h|e|0.059
  M j:"minimal_task"
  M k:"tasks"
  M l:"x:\\robocorpws\\vscode-robot-tests\\PythonFmk\\tasks.py"
  M m:null
  P i:j|k|l|m|7
  ST i|0.059
  M n:"============================ "
  C f|n|0.059
  M o:"Running: "
  C f|o|0.059
  M p:"task_name"
  C p|j|0.059
  M q:" =============================\n"
  C f|q|0.059
  P r:j|k|l|e|9
  M s:"METHOD"
  SE r|s|0.059
  M t:"message"
  M u:"str"
  M v:"'Hello'"
  AS r|t|u|v|0.062
  P w:j|k|l|e|10
  M x:"'Hello World!'"
  AS w|t|u|x|0.062
  M z:"some_method"
  P y:z|k|l|e|5
  SE y|s|0.062
  M A:"stdout"
  M B:"here"
  C A|B|0.062
  M C:"\n"
  C A|C|0.063
  EE s|h|0.063
  M E:"for i in range(10)"
  P D:E|k|l|e|13
  M F:"FOR"
  SE D|F|0.063
  P G:E|k|l|e|14
  M H:"FOR_STEP"
  SE G|H|0.063
  M I:"i"
  M J:"int"
  M K:"0"
  EA I|J|K
  C A|K|0.078
  C A|C|0.078
  M L:"stderr"
  M M:"err"
  C L|M|0.078
  C L|C|0.079
  EE H|h|0.079
  SE G|H|0.079
  M N:"1"
  EA I|J|N
  C A|N|0.094
  C A|C|0.094
  C L|M|0.094
  C L|C|0.095
  EE H|h|0.095
  SE G|H|0.095
  M O:"2"
  EA I|J|O
  C A|O|0.109
  C A|C|0.109
  C L|M|0.11
  C L|C|0.11
  EE H|h|0.11
  SE G|H|0.11
  M P:"3"
  EA I|J|P
  C A|P|0.125
  C A|C|0.125
  C L|M|0.125
  C L|C|0.125
  EE H|h|0.125
  SE G|H|0.125
  M Q:"4"
  EA I|J|Q
  C A|Q|0.14
  C A|C|0.14
  C L|M|0.14
  C L|C|0.14
  EE H|h|0.14
  SE G|H|0.14
  M R:"5"
  EA I|J|R
  C A|R|0.156
  C A|C|0.157
  C L|M|0.157
  C L|C|0.157
  EE H|h|0.157
  SE G|H|0.157
  M S:"6"
  EA I|J|S
  C A|S|0.171
  C A|C|0.171
  C L|M|0.171
  C L|C|0.171
  EE H|h|0.171
  SE G|H|0.171
  M T:"7"
  EA I|J|T
  C A|T|0.187
  C A|C|0.187
  C L|M|0.187
  C L|C|0.187
  EE H|h|0.187
  SE G|H|0.187
  M U:"8"
  EA I|J|U
  C A|U|0.202
  C A|C|0.202
  C L|M|0.202
  C L|C|0.202
  EE H|h|0.202
  SE G|H|0.203
  M V:"9"
  EA I|J|V
  C A|V|0.218
  C A|C|0.218
  C L|M|0.218
  C L|C|0.218
  EE H|h|0.218
  EE F|h|0.218
  EE s|h|0.218
  C p|j|0.218
  M W:" status: "
  C f|W|0.218
  M X:"PASS\n"
  C f|X|0.219
  M Y:"================================================================================\n"
  C f|Y|0.219
  ET h|e|0.219
  M aa:"Teardown tasks"
  M ab:"teardown"
  P Z:aa|ab|e|e|0
  ST Z|0.219
  M ac:"Process snapshot"
  SPS ac|0.219
  M ad:"System information:\nMemory: Total: 38.8 G, Available: 20.7 G, Used: 46.7 %\nCPUs: 12"
  P ae:e|e|e|e|0
  L I|ad|ae|0|0.416
  M af:"Current Process: python.exe (pid: 20940, status: running)\nCommand Line: c:\\ProgramData\\robocorp\\ht\\545e18d_b1f3c24_91bb43ea\\python.exe -m robocorp.tasks run x:\\robocorpws\\vscode-robot-tests\\PythonFmk\\tasks.py -t minimal_task\nStarted: 08:50:52\nParent pid: 4280\nResident Set Size: 27.9 M\nVirtual Memory Size: 18.7 M"
  L I|af|ae|0|0.433
  M ag:"MainThread|Thread ID: 17148 (non daemon)"
  STD ag|0.434
  M ah:"c:\\ProgramData\\robocorp\\ht\\545e18d_b1f3c24_91bb43ea\\lib\\site-packages\\robocorp\\log\\__init__.py"
  M ai:"process_snapshot"
  M aj:"robo_logger.process_snapshot()"
  TBE ah|179|ai|aj
  M ak:"logger_instances"
  M al:"dict"
  M am:"{<robocorp.log._robo_logger._RoboLogger object at 0x0000020C98D649D0>: 1, <robocorp.log._robo_logger._RoboLogger object at 0x0000020C982259A0>: 1}"
  TBV ak|al|am
  M an:"robo_logger"
  M ao:"_RoboLogger"
  M ap:"<robocorp.log._robo_logger._RoboLogger object at 0x0000020C98D649D0>"
  TBV an|ao|ap
  M aq:"c:\\ProgramData\\robocorp\\ht\\545e18d_b1f3c24_91bb43ea\\lib\\site-packages\\robocorp\\log\\_robo_logger.py"
  M ar:"new_func"
  M as:"return func(self, *args, **kwargs)"
  TBE aq|20|ar|as
  M at:"self"
  TBV at|ao|ap
  M au:"args"
  M av:"tuple"
  M aw:"()"
  TBV au|av|aw
  M ax:"kwargs"
  M ay:"{}"
  TBV ax|al|ay
  M az:"func"
  M aA:"function"
  M aB:"<function _RoboLogger.process_snapshot at 0x0000020C98C7D3A0>"
  TBV az|aA|aB
  M aC:"return self._robot_output_impl.process_snapshot(hide_vars)"
  TBE aq|410|ai|aC
  TBV at|ao|ap
  M aD:"hide_vars"
  M aE:"bool"
  M aF:"False"
  TBV aD|aE|aF
  M aG:"c:\\ProgramData\\robocorp\\ht\\545e18d_b1f3c24_91bb43ea\\lib\\site-packages\\robocorp\\log\\_robo_output_impl.py"
  M aH:"self._dump_threads(hide_vars)"
  TBE aG|746|ai|aH
  TBV aD|aE|aF
  M aI:"log"
  M aJ:"module"
  M aK:"<module 'robocorp.log' from 'c:\\\\ProgramData\\\\robocorp\\\\ht\\\\545e18d_b1f3c24_91bb43ea\\\\lib\\\\site-packages\\\\robocorp\\\\log\\\\__init__.py'>"
  TBV aI|aJ|aK
  M aL:"entry_id"
  M aM:"'ps_0'"
  TBV aL|u|aM
  M aN:"entry_type"
  M aO:"'process_snapshot'"
  TBV aN|u|aO
  M aP:"psutil"
  M aQ:"<module 'psutil' from 'c:\\\\ProgramData\\\\robocorp\\\\ht\\\\545e18d_b1f3c24_91bb43ea\\\\lib\\\\site-packages\\\\psutil\\\\__init__.py'>"
  TBV aP|aJ|aQ
  M aR:"AccessDenied"
  M aS:"type"
  M aT:"<class 'psutil.AccessDenied'>"
  TBV aR|aS|aT
  M aU:"NoSuchProcess"
  M aV:"<class 'psutil.NoSuchProcess'>"
  TBV aU|aS|aV
  M aW:"ZombieProcess"
  M aX:"<class 'psutil.ZombieProcess'>"
  TBV aW|aS|aX
  M aY:"curr_process"
  M aZ:"Process"
  M a0:"psutil.Process(pid=20940, name='python.exe', status='running', started='08:50:52')"
  TBV aY|aZ|a0
  M a1:"log_info"
  M a2:"<function _RoboOutputImpl.process_snapshot.<locals>.log_info at 0x0000020C9A5E2040>"
  TBV a1|aA|a2
  M a3:"memory_info"
  M a4:"'Total: 38.8 G, Available: 20.7 G, Used: 46.7 %'"
  TBV a3|u|a4
  M a5:"child_i"
  TBV a5|J|K
  M a6:"child"
  TBV a6|aZ|a0
  M a7:"name"
  M a8:"'python.exe'"
  TBV a7|u|a8
  M a9:"status"
  M ba:"'running'"
  TBV a9|u|ba
  M bb:"create_time"
  M bc:"'08:50:52'"
  TBV bb|u|bc
  M bd:"ppid"
  M be:"'4280'"
  TBV bd|u|be
  M bf:"cmdline"
  M bg:"'c:\\\\ProgramData\\\\robocorp\\\\ht\\\\545e18d_b1f3c24_91bb43ea\\\\python.exe -m robocorp.tasks run x:\\\\robocorpws\\\\vscode-robot-tests\\\\PythonFmk\\\\tasks.py -t minimal_task'"
  TBV bf|u|bg
  M bh:"rss"
  M bi:"'27.9 M'"
  TBV bh|u|bi
  M bj:"vms"
  M bk:"'18.7 M'"
  TBV bj|u|bk
  M bl:"proc_memory_info"
  M bm:"pmem"
  M bn:"pmem(rss=29229056, vms=19587072, num_page_faults=29106, peak_wset=29937664, wset=29229056, peak_paged_pool=155888, paged_pool=155712, peak_nonpaged_pool=21464, nonpaged_pool=21328, pagefile=19587072, peak_pagefile=20701184, private=19587072)"
  TBV bl|bm|bn
  M bo:"'Current Process: python.exe (pid: 20940, status: running)\\nCommand Line: c:\\\\ProgramData\\\\robocorp\\\\ht\\\\545e18d_b1f3c24_91bb43ea\\\\python.exe -m robocorp.tasks run x:\\\\robocorpws\\\\vscode-robot-tests\\\\PythonFmk\\\\tasks.py -t minimal_task\\nStarted: 08:50:52\\nParent pid: 4280\\nResident Set Size: 27.9 M\\nVirtual Memory Size: 18.7 M'"
  TBV t|u|bo
  M bp:"_RoboOutputImpl"
  M bq:"<robocorp.log._robo_output_impl._RoboOutputImpl object at 0x0000020C97C77CA0>"
  TBV at|bp|bq
  M br:"_dump_threads"
  M bs:"stack.append((f, f.f_lineno))"
  TBE aG|764|br|bs
  TBV at|bp|bq
  TBV aD|aE|aF
  M bt:"thread_id"
  M bu:"17148"
  TBV bt|J|bu
  M bv:"frame"
  M bw:"<frame at 0x0000020C981C0BB0, file 'c:\\\\ProgramData\\\\robocorp\\\\ht\\\\545e18d_b1f3c24_91bb43ea\\\\lib\\\\site-packages\\\\robocorp\\\\log\\\\_robo_output_impl.py', line 768, code _dump_threads>"
  TBV bv|bv|bw
  M bx:"thread"
  M by:"_MainThread"
  M bz:"<_MainThread(MainThread, started 17148)>"
  TBV bx|by|bz
  M bA:"title"
  M bB:"'MainThread|Thread ID: 17148 (non daemon)'"
  TBV bA|u|bB
  M bC:"f"
  M bD:"<frame at 0x0000020C9798D490, file 'c:\\\\ProgramData\\\\robocorp\\\\ht\\\\545e18d_b1f3c24_91bb43ea\\\\lib\\\\site-packages\\\\robocorp\\\\tasks\\\\_commands.py', line 242, code run>"
  TBV bC|bv|bD
  M bE:"stack"
  M bF:"list"
  M bG:"[(<frame at 0x0000020C9A6D4B20, file 'c:\\\\ProgramData\\\\robocorp\\\\ht\\\\545e18d_b1f3c24_91bb43ea\\\\lib\\\\site-packages\\\\robocorp\\\\log\\\\__init__.py', line 179, code process_snapshot>, 179), (<frame at 0x0000020C97F67810, file 'c:\\\\ProgramData\\\\robocorp\\\\ht\\\\545e18d_b1f3c24_91bb43ea\\\\lib\\\\site-packages\\\\robocorp\\\\log\\\\_robo_logger.py', line 20, code new_func>, 20), (<frame at 0x0000020C9A60B550, file 'c:\\\\ProgramData\\\\robocorp\\\\ht\\\\545e18d_b1f3c24_91bb43ea\\\\lib\\\\site-packages\\\\robocorp\\\\log\\\\_robo_logger.py', line 410, code process_snapshot>, 410), (<frame at 0x0000020C981DA010, file 'c:\\\\ProgramData\\\\robocorp\\\\ht\\\\545e18d_b1f3c24_91bb43ea\\\\lib\\\\site-packages\\\\robocorp\\\\log\\\\_robo_output_impl.py', line 746, code process_snapshot>, 746), (<frame at 0x0000020C981C0BB0, file 'c:\\\\ProgramData\\\\robocorp\\\\ht\\\\545e18d_b1f3c24_91bb43ea\\\\lib\\\\site-packages\\\\robocorp\\\\log\\\\_robo_output_impl.py', line 768, code _dump_threads>, 764)]"
  TBV bE|bF|bG
  ETD 0.446
  EPS 0.446
  ET h|e|0.483
  ER h|0.483
  `;
  const s = JSON.stringify(raw);
  return JSON.parse(s);
}

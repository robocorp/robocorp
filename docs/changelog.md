New in 0.0.6 (2022-02-10)
-----------------------------

- Fixed issue where stopping logging would not add the start keyword but would end up adding the end keyword.


New in 0.0.5 (2022-02-09)
-----------------------------

- Fixed one issue generating the output from the standard Robot Framework XML.
- Added API to stop and start logging methods or keyword arguments.
- Added API to add a string to be hidden from the logs.
- Hiding information through tags in methods (`log:ignore-variables` and `log:ignore-methods`).
- Automatically hide the contents of variables named `*password*` or `*passwd*`. 


New in 0.0.4 (2022-12-13)
-----------------------------

- Improved handling in case some internal exception happens.


New in 0.0.3 (2022-12-06)
-----------------------------

- Properly added `py.typed` file to release.
 

New in 0.0.2 (2022-11-30)
-----------------------------

- `LH` message type added to provide embedded html (i.e.: add images to log output).
- `ID` provides an id for the run and the part of the file (incremented when rotating the output). 

- `log.html` improvements:

  - Can filter out methods with `NOT RUN` status.
  - Hides iteration nodes after the 50th iteration (only if marked as `PASS` or `NOT RUN`).
  - Embeds HTML contents from log entries with `html=true`. 


New in 0.0.1 (2022-11-22)
-----------------------------

### First release

- Note: pre-alpha for early adapters.
- Format may still change.
- Basic structure which allows to memoize strings and build suite/task,test/keyword scope.
- Provides status, time, rotating output, tags, keyword arguments.
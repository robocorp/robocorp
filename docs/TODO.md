# Fabio's TODO

# DONE

- Logging: Failure handling:
    - Mark as failed

# WORK IN PROGRESS

- Logging: Thread handling (done but needs tests)
    - V1: just log main thread
    
- Logging: Create API to add to log text messages in different log levels (done but needs tests)


# What must be done prior to an alpha release (python framework/logging)

- Logging: Failure handling:
    - Show message regarding failure
    - Show tracebacks with variables from scope


- Logging: Create API to add to log html messages.
    - Note: internally log html messages are already supprted, but maybe we should
      also make sure that the html being added is safe -- i.e.: support img, table
      but not script?.Need to evaluate use cases and whether there's a safety concern
      here (right now clients of the API need to be careful of injection attacks
      and the API just adds as html what's passed).

- Logging: Provide option to style with Janne's changes.

- Logging: Change to use poetry and do first pypi release.

- Create at least basic end-to-end integration test (`test_example_works.py` is currently skipped).


# Maybe

- Move logging into the framework monorepo?

    
# After first alpha

- Cli: receive compacted message and uncompact it afterwards instead of receiving
  it already uncompacted (i.e.: send internal format and not json in the wire).
  - decoding may need a new public API for this.

- Log return values.

- Provide docstrings in the log.html

- VSCode integration:
    - Connect through port.

- Configure timeout for running
    - On timeout stop execution (as gracefully as possible).
    - On timeout provide thread dump on the logs.
    
- Logging: Thread handling:
    - V2: log other threads too

- Log control statements:
    - If / While / For
    
- Log variable assignments.

# Performance improvements:

- Cythonized version for faster logging (overhead can be considerable).
- Right now we have multiple logger instances and call methods for each one
  and each one has to repack the messages being sent. Maybe we could have a
  single one that outputs to multiple streams.



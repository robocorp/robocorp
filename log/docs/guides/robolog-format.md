# The `.robolog` format

## Disclaimer

The format documented below may not be stable across versions and compatibility
may be broken as the format evolves.

## Requirements

The requirements for the generated log files are the following:

1. Compact log:

    The files generated should be as compact as possible. Reading the file
    may require a separate application (although the idea is still -- initially
    -- trying to keep to ASCII instead of a binary format).

2. Log streaming:

    The log format should be suitable for streaming (so, it's possible to
    interpret the log while it's being written or up to the point a 
    Python VM crash happened).

3. Information:

    While the format of the log should be as compact as possible, it should 
    be able to provide the needed information to debug an issue, so,
    it must track quite a bit of information from a python run.

4. Log file rotation:

    If while being written a log becomes too big the log contents should be
    rotated to a separate file and it should be possible to specify a maximum
    size for the log (even if old information in the log is discarded in this
    case).

## Outputs

The basic log can actually be split into multiple files.
Such files are splitted in the following files (the idea is that it can be split when it becomes too big).

- `output.robolog`
- `output_2.robolog`
- `output_3.robolog`
- ...

The file should be always written and flushed at each log entry and it should be consistent even if the process crashes in the meanwhile (meaning that all entries written are valid up to the point of the crash).

## Log spec (parser generated from the spec below)

    # Each message should use a single line in the log output where the prefix
    # is the message type and the arguments is either a message with ids/numbers
    # separated by '|' or json-encoded strings.
    #
    # Note that each output log file (even if splitted after the main one) should be
    # readable in a completely independent way, so, the starting scope should be
    # replicated as well as the needed names to memorize.
    #
    # To keep the format compact, some strings and locations are referenced through ids. 
    # 
    # In the spec 'oid' are used to reference a message memorized with 'M' and 
    # 'loc_id' or 'loc_and_doc_id' a message memorized with 'P'.
    #
    # There's an initial time and other time references are time-deltas from this time.
    #
    # The spec for the messages is below:
    #
    
    # Version of the log output
    # Example: 'V 0.0.1' - Identifies version 1 of the log
    V: version:str
    
    # Some information message
    # Example: 'I "python=3.7"'
    I: info:json.loads
    
    # The log has an id that may be split into multiple parts.
    # 'ID: 1|36ac1f85-6d32-45b0-8ebf-3bbf8d7482f2'     1st part with identifier 36ac1f85-6d32-45b0-8ebf-3bbf8d7482f2.
    # 'ID: 2|36ac1f85-6d32-45b0-8ebf-3bbf8d7482f2'     2nd part with identifier 36ac1f85-6d32-45b0-8ebf-3bbf8d7482f2.
    ID: part:int, id:str
    
    # Initial time in UTC (all others are based on a delta from this date).
    # Example: 'T 2022-10-03T11:30:54.927+00:00'
    T: time:dateisoformat
    
    # Memorize some word (to be used as oid).
    # i.e.: when the message is something as 'M a:"Start"', we memorize "Start" with key: "a"
    # Example: 'M a:"Start"'
    M: memorize
    
    # Memorize a path location (name/libname/source/lineno/docstring) to be referenced as loc_id or loc_and_doc_id.
    # Note: loc_id and loc_and_doc_id use the same info but one unpacks the docstring and the other doesn't
    # Example: 'P a|b|c|d|e' (where those are references to strings memoized with 'M').
    P: memorize_path
    
    # Log (raw text)
    # level_enum is:
    # - ERROR = 'E'
    # - FAIL = 'F'
    # - INFO = 'I'
    # - WARN = 'W'
    #
    # Example:
    #
    # 'L E|a|b|0.123'
    L: level:str, message:oid, loc:loc_id, time_delta_in_seconds:float
    
    # A message which is intended to be sent to to the console
    # This can be either a message being sent by the user to stdout/stderr
    # (if those are being redirected) or some message from the framework
    # intended to be shown in the console.
    #
    # Expected "kind" values:
    #
    # User messages:
    # "stdout": Some user message which was being sent to the stdout.
    # "stderr": Some user message which was being sent to the stderr.
    #
    # Messages from the framework:
    # "regular": Some regular message.
    # "important": Some message which deserves a bit more attention.
    # "task_name": The task name is being written.
    # "error": Some error message.
    # "traceback": Some traceback message.
    #
    # Example:
    #
    # 'C a|b|0.123'
    C: kind:oid, message:oid, time_delta_in_seconds:float
    
    # Log (html) -- same thing as Log but the message must be interpreted as HTML.
    # So, something as <img alt="screenshot" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAABAAAAAEgCAIAAACl65ZFAAEAAElEQVR4nOz9d7R..."/>
    # would be interpreted as an image in the final HTML. 
    LH=L
    
    # Start Run
    SR: name:oid, time_delta_in_seconds:float
    
    # End Run
    ER: status:oid, time_delta_in_seconds:float
    
    # Start Task
    ST: loc:loc_id, time_delta_in_seconds:float
    
    # End Task
    # status may be:
    # "PASS": Everything went well.
    # "ERROR": There was some detected error while running the task.
    ET: status:oid, message:oid, time_delta_in_seconds:float
    
    # Start Element 
    # Should be sent when some element we're tracking such as method, for, while, etc. starts.
    # The 'type' can be:
    #
    # METHOD
    #
    # GENERATOR
    #
    # UNTRACKED_GENERATOR (untracked generator is a generator in a library, where we
    # just track the start/end and not what happens inside it).
    #
    # FOR
    # FOR_STEP
    SE: loc:loc_and_doc_id, type:oid, time_delta_in_seconds:float
    
    # Yield Resume (coming back to a suspended frame).
    # Should be sent when a given frame is resumed from a yield.
    YR: loc:loc_id, time_delta_in_seconds:float
    
    # Yield From Resume (coming back to a suspended frame).
    # Should be sent when a given frame is resumed from a yield from.
    YFR: loc:loc_id, time_delta_in_seconds:float
    
    # End Element
    # When the element ends, provide its status ("PASS", "ERROR") and the time at which it finished.
    EE: type:oid, status:oid, time_delta_in_seconds:float
    
    # Yield Suspend (pausing a frame)
    # Should be sent when a given frame is suspended in a yield.
    YS: loc:loc_id, type:oid, value:oid, time_delta_in_seconds:float
    
    # Yield From Suspend (pausing a frame)
    # Should be sent when a given frame is suspended in a yield from.
    YFS: loc:loc_id, time_delta_in_seconds:float
    
    # Assign
    # Assign some content (type, value) to a variable (target) in the given location (loc). 
    AS: loc:loc_id, target:oid, type:oid, value:oid, time_delta_in_seconds:float
    
    # Element/method argument (name and value of the argument).
    # If it's a FOR, this is the target of the for.
    # Adds some argument (name) to the current element (with the given type and value).
    EA: name:oid, type:oid, value:oid
    
    # Set some time for the current scope (usually not needed as the time
    # is usually given in the element itself).
    S: start_time_delta:float
    
    # --------------------------------------------------------------- Tracebacks
    # Start traceback with the exception error message.
    # Note: it should be possible to start a traceback inside another traceback
    # for cases where the exception has an exception cause.
    
    # Start Traceback
    STB: message:oid, time_delta_in_seconds:float
    
    # Traceback Entry
    TBE: source:oid, lineno:int, method:oid, line_content:oid
    
    # Traceback variable
    TBV: name:oid, type:oid, value:oid
    
    # End Traceback
    ETB: time_delta_in_seconds:float
    
    # ---------------------------------------------------------- Process snapshots
    # Process snapshots mean that a dump with information of the current
    # process was requested. The idea is that the 'start process snapshot' message
    # is sent and then a number of 'log info' messages are sent with details on the
    # process (such as memory, subprocesses, etc) and then a thread dump is created
    # (very close to a traceback but the kind is different and the message is not
    # the exception message but contains information on the thread dumped).
    
    # Start process snapshot 
    SPS: message:oid, time_delta_in_seconds:float
    # End process snapshot 
    EPS: time_delta_in_seconds:float
    
    # Start thread dump (message has thread name/info)
    STD=STB
    # End thread dump
    ETD=ETB
    
    # These messages have the same format (just the message type is different).
    # Restart Run
    RR=SR
    # Restart Test
    RT=ST
    # Restart Entry
    RE=SE
    # Restart traceback
    RTB=STB
    # Restart yield resume
    RYR=YR
    # Restart yield from resume
    RYFR=YFR
    # Restart process snapshot
    RPS=SPS
    # Restart thread dump
    RTD=STD

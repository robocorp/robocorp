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


## "Basic log" spec

To keep the format compact, strings will be referenced by an id in the output and the output message types will be predetermined and referenced in the same way.

Times are referenced by the delta from the start.

Also, each message should use a single line in the log output where the prefix is the message type and the arguments is either a message with ids/numbers separated by `|` or json-encoded strings.

Note that each output log file (even if splitted after the main one) should be readable in a completely independent way, so, the starting scope should be replicated as well as the needed names to memorize.

Basic message types are:

### V: Version(name)

    Identifies the version of the log being used
    
    Example:
    
    `V 0.0.1`             - Identifies version 1 of the log

### ID: Identifier and part for this run.

    Provides a unique id for the run (which should be the same even if the
    file is split among multiple files) as well as the identification of
    which is the current part.
    
    Example:
    
    `ID: 1|36ac1f85-6d32-45b0-8ebf-3bbf8d7482f2`     1st part with identifier 36ac1f85-6d32-45b0-8ebf-3bbf8d7482f2.
    `ID: 2|36ac1f85-6d32-45b0-8ebf-3bbf8d7482f2`     2nd part with identifier 36ac1f85-6d32-45b0-8ebf-3bbf8d7482f2.

### I: Info(info_as_json_string)

    Example:
    
    `I "python=3.7"`
    `I "RF=5.7.0"`

### M: Memorize name(id ':' json_string)

    Example:

    `M a:"Start Suite"`    - Identifies the String 'Start Suite' as 'a' in the logs 
    `M b:"End Suite"`      - Identifies the String 'End Suite' as 'b' in the logs

### T: Initial time(isoformat)

    Example:
    
    `T 2022-10-03T11:30:54.927`

### SR: Start Run

    Spec: `name:oid, time_delta_in_seconds:float`
    
    Note: references to oid mean a reference to a previously memorized name.
    
    Note: the time may be given as -1 (if unknown -- later it may be provided
    through an "S" message to specify the start time which may be useful
    when converting to xml where the status only appears later on in the file
    along with the status and not at the suite definition).
    
    Example (were a is a reference to a previously memorized name):
    
    `SR a|0.333`

## RR: Replay Start Run

    Same as "SR" but used just to replay the content to specify the context
    when the log starts being written in a new file.

### ER: End Run

    Spec: `status:oid, time_delta_in_seconds:float`
    
    Note: the status (PASS, FAIL, SKIP) is a previously memorized name.
    
    Example:
    
    `ER a|0.222`

### ST: Start Task

    Spec: `name:oid, suite_id:oid, lineno:int, time_delta_in_seconds:float`
    
    Note: the source (filename) is available through the parent suite_source.
    
    Example:
    
    `ST a|b|22|0.332`

## RT: Replay Start Task

    Same as "ST" but used just to replay the content to specify the context
    when the log starts being written in a new file.


### ET: End Task

    Spec: `status:oid, message:oid, time_delta_in_seconds:float`
    
    Example:
    
    `ET a|b|0.332`

### SE: Start Element

    Spec: `name:oid, libname:oid, type:oid, doc:oid, source:oid, lineno:int, time_delta_in_seconds:float`
    
    Example:
    
    `SE a|b|c|d|e|22|0.444`

## RE: Replay Element

    Same as "SE" but used just to replay the content to specify the context
    when the log starts being written in a new file.

### EA: Element argument

    Spec: `name:oid, type:oid, value:oid`
    
    Example:
    
    `EA f|g|h`

### AS: Assign some content to a variable.

    Spec: `source:oid, lineno:int, target:oid, type:oid, value:oid, time_delta_in_seconds:float`
    
### EE: End Element

    Spec: `type:oid, status:oid, time_delta_in_seconds:float`
    
    Example:
    
    `EE a|0.333`

### L: Provide a log message

    Spec: `level:level_enum, message:oid, time_delta_in_seconds:float`
    
    level_enum is:
    - ERROR = `E`
    - FAIL = `F`
    - INFO = `I`
    - WARN = `W`
    
    Example:
    
    `L E|a|0.123`

### LH: Provide an html log message

    Same as "L" but interned message is expected to be an html which can be
    embedded in the final log.html.
    
    i.e.: the message can be something as:
    
    <img alt="screenshot" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAABAAAAAEgCAIAAACl65ZFAAEAAElEQVR4nOz9d7R..."/>
    
    In which case the img would be embedded as an image in the final log.html.

### S: Specify the start time (of the containing run/task/element)

    Spec: `start_time_delta:float`
    
    Example:
    
    `S 2.456`

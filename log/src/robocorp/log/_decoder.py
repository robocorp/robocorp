import json
from typing import Optional, List, Callable, Any, Dict, Iterator, Tuple
from .protocols import IReadLines
import datetime

# Whenever the decoding changes we should bump up this version.
DOC_VERSION = "0.0.2"

# name, libname, source, docstring, lineno
Location = Tuple[str, str, str, str, int]


class Decoder:
    def __init__(self) -> None:
        self.memo: Dict[str, str] = {}
        self.location_memo: Dict[str, Location] = {}

    def decode_message_type(self, message_type: str, message: str) -> Optional[dict]:
        handler = _MESSAGE_TYPE_INFO[message_type]
        ret = {"message_type": message_type}
        try:
            r = handler(self, message)
            if not r:
                if message_type in ("M", "P"):
                    return None
                raise RuntimeError(
                    f"No return when decoding: {message_type} - {message}"
                )
                if not isinstance(r, dict):
                    ret[
                        "error"
                    ] = f"Expected dict return when decoding: {message_type} - {message}. Found: {ret}"

            ret.update(r)
        except Exception as e:
            ret["error"] = f"Error decoding: {message_type}: {e}"
        return ret


def _decode_oid(decoder: Decoder, oid: str) -> str:
    return decoder.memo[oid]


def _decode_float(decoder: Decoder, msg: str) -> float:
    return float(msg)


def _decode_int(decoder: Decoder, msg: str) -> int:
    return int(msg)


def _decode_str(decoder: Decoder, msg: str) -> str:
    return msg


def _decode_json(decoder: Decoder, msg: str) -> str:
    return json.loads(msg)


def _decode_dateisoformat(decoder: Decoder, msg: str) -> str:
    d: datetime.datetime = datetime.datetime.fromisoformat(msg)
    # The internal time is in utc, so, we need to decode it to the current timezone.
    d = d.astimezone()
    return d.isoformat(timespec="milliseconds")


def _decode(message_definition: str) -> Callable[[Decoder, str], Any]:
    if message_definition == "memorize":
        return decode_memo
    elif message_definition == "memorize_path":
        return decode_path_location

    names: List[str] = []
    name_to_decode: dict = {}
    for s in message_definition.split(","):
        s = s.strip()
        i = s.find(":")
        if i != -1:
            s, decode = s.split(":", 1)
        else:
            raise AssertionError(f"Unexpected definition: {message_definition}")

        names.append(s)
        if decode == "oid":
            name_to_decode[s] = _decode_oid

        elif decode == "int":
            name_to_decode[s] = _decode_int

        elif decode == "float":
            name_to_decode[s] = _decode_float

        elif decode == "str":
            name_to_decode[s] = _decode_str

        elif decode == "json.loads":
            name_to_decode[s] = _decode_json

        elif decode == "dateisoformat":
            name_to_decode[s] = _decode_dateisoformat

        elif decode == "loc_id":
            name_to_decode[s] = "loc_id"

        elif decode == "loc_and_doc_id":
            name_to_decode[s] = "loc_and_doc_id"

        else:
            raise RuntimeError(f"Unexpected: {decode}")

    def dec_impl(decoder: Decoder, message: str):
        splitted = message.split("|", len(names) - 1)
        ret: Dict[str, Any] = {}
        for i, s in enumerate(splitted):
            name = names[i]
            try:
                dec_func = name_to_decode[name]
                if dec_func == "loc_id":
                    info = decoder.location_memo[s]
                    ret["name"] = info[0]
                    ret["libname"] = info[1]
                    ret["source"] = info[2]
                    ret["lineno"] = info[4]

                elif dec_func == "loc_and_doc_id":
                    info = decoder.location_memo[s]
                    ret["name"] = info[0]
                    ret["libname"] = info[1]
                    ret["source"] = info[2]
                    ret["doc"] = info[3]
                    ret["lineno"] = info[4]

                else:
                    ret[name] = dec_func(decoder, s)
            except:
                ret[name] = None
        return ret

    return dec_impl


def decode_memo(decoder: Decoder, message: str) -> None:
    """
    Args:
        message: something as 'a:"Start Suite"'
    """
    memo_id: str
    memo_value: str

    memo_id, memo_value = message.split(":", 1)

    # Note: while the json.loads could actually load anything, in the spec we only
    # have oid for string messages (which is why it's ok to type it as that).
    memo_value = json.loads(memo_value)
    decoder.memo[memo_id] = memo_value


def decode_path_location(decoder: Decoder, message: str) -> None:
    """
    Args:
        message: something as 'a:b|c|d|e|33'
    """
    memo_id, memo_references = message.split(":", 1)
    name_id, libname_id, source_id, doc_id, lineno = memo_references.split("|", 4)

    decoder.location_memo[memo_id] = (
        decoder.memo[name_id],
        decoder.memo[libname_id],
        decoder.memo[source_id],
        decoder.memo[doc_id],
        int(lineno),
    )


MESSAGE_TYPE_YIELD_RESUME = "YR"
MESSAGE_TYPE_YIELD_SUSPEND = "YS"
MESSAGE_TYPE_YIELD_FROM_RESUME = "YFR"
MESSAGE_TYPE_YIELD_FROM_SUSPEND = "YFS"

# Note: the spec appears in 3 places (and needs to be manually updated accordingly).
# _decoder.py (this file)
# decoder.ts
# format.md

SPEC = """ 
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

# These messages have the same format (just the message type is different).
RR=SR
RT=ST
RE=SE
RTB=STB
RYR=YR
"""

_MESSAGE_TYPE_INFO: Dict[str, Callable[[Decoder, str], Any]] = {}


def _build_decoding():
    for line in SPEC.splitlines(keepends=False):
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        try:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip()
        except ValueError:
            # No ':' there, must be = msg
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip()
            _MESSAGE_TYPE_INFO[key] = _MESSAGE_TYPE_INFO[val]
        else:
            _MESSAGE_TYPE_INFO[key] = _decode(val)


_build_decoding()


def iter_decoded_log_format(stream: IReadLines) -> Iterator[dict]:
    decoder: Decoder = Decoder()
    line: str
    message_type: str
    message: str
    decoded: Optional[dict]

    for line in stream.readlines():
        line = line.strip()
        if line:
            try:
                message_type, message = line.split(" ", 1)
            except:
                raise RuntimeError(f"Error decoding line: {line}")
            decoded = decoder.decode_message_type(message_type, message)
            if decoded:
                yield decoded

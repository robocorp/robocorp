// Based on the python decoder example.
// Used: https://extendsclass.com/python-to-javascript.html

import parseISO from "date-fns/parseISO";

export interface IMessage {
    readonly message_type: string;
    readonly decoded: any;
}

function _decode_dateisoformat(decoder, time) {
    const parsedTime = parseISO(time);
    // Note: doing toString() in an utc time (which ends with +00:00)
    // will convert it to the local timezone.
    return parsedTime.toString();
}

function decode_memo(decoder, message) {
    var memo_id, memo_value;
    const split = splitInChar(message, ":");
    if (split) {
        [memo_id, memo_value] = split;
        try {
            memo_value = JSON.parse(memo_value);
        } catch (error) {
            console.log("Error parsing json: " + memo_value);
            console.log(error);
            return null;
        }
        decoder.memo[memo_id] = memo_value;
    }

    return null;
}

function decode_path_location(decoder, message) {
    const [memo_id, memo_references] = splitInChar(message, ":");
    const [name_id, libname_id, source_id, doc_id, lineno] = memo_references.split("|", 5);

    decoder.location_memo[memo_id] = [
        decoder.memo[name_id],
        decoder.memo[libname_id],
        decoder.memo[source_id],
        decoder.memo[doc_id],
        parseInt(lineno),
    ];
}

function _decodeOid(decoder, oid) {
    const ret = decoder.memo[oid];
    if (ret === undefined) {
        return `<ref not found: ${oid}>`;
    }
    return ret;
}

function _decodeFloat(decoder, msg) {
    return parseFloat(msg);
}

function _decodeInt(decoder, msg) {
    return parseInt(msg);
}

function _decodeStr(decoder, msg) {
    return msg;
}

function _decodeJson(decoder, msg) {
    return JSON.parse(msg);
}

function _decode(message_definiton) {
    if (message_definiton === "memorize") {
        return decode_memo;
    } else if (message_definiton === "memorize_path") {
        return decode_path_location;
    }
    const names = [];
    const nameToDecode = new Map();
    for (let s of message_definiton.split(",")) {
        s = s.trim();
        const i = s.indexOf(":");
        let decode;
        if (i != -1) {
            [s, decode] = s.split(":", 2);
        } else {
            throw new Error(`Unexpected definition: {message_definition}`);
        }

        names.push(s);
        if (decode === "oid") {
            nameToDecode.set(s, _decodeOid);
        } else if (decode === "int") {
            nameToDecode.set(s, _decodeInt);
        } else if (decode === "float") {
            nameToDecode.set(s, _decodeFloat);
        } else if (decode === "str") {
            nameToDecode.set(s, _decodeStr);
        } else if (decode === "json.loads") {
            return _decodeJson;
        } else if (decode === "dateisoformat") {
            return _decode_dateisoformat;
        } else if (decode === "loc_id") {
            nameToDecode.set(s, "loc_id");
        } else if (decode === "loc_and_doc_id") {
            nameToDecode.set(s, "loc_and_doc_id");
        } else {
            throw new Error("Unexpected: " + decode);
        }
    }

    function _decImpl(decoder, message) {
        const splitted = message.split("|", names.length);
        const ret = {};
        for (let index = 0; index < splitted.length; index++) {
            const s = splitted[index];
            const name = names[index];
            const decFunc = nameToDecode.get(name);
            if (decFunc === "loc_id") {
                const info = decoder.location_memo[s];
                ret["name"] = info[0];
                ret["libname"] = info[1];
                ret["source"] = info[2];
                ret["lineno"] = info[4];
            } else if (decFunc === "loc_and_doc_id") {
                const info = decoder.location_memo[s];
                ret["name"] = info[0];
                ret["libname"] = info[1];
                ret["source"] = info[2];
                ret["doc"] = info[3];
                ret["lineno"] = info[4];
            } else {
                ret[name] = decFunc(decoder, s);
            }
        }
        // console.log("decoded", ret);
        return ret;
    }
    return _decImpl;
}

const _MESSAGE_TYPE_INFO = {};

function buildDecoding() {
    const SPEC = `
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
`;
    for (let line of SPEC.split(/\r?\n/)) {
        line = line.trim();
        if (line.length === 0 || line.startsWith("#")) {
            continue;
        }

        try {
            let [key, val] = splitInChar(line, ":");
            key = key.trim();
            val = val.trim();
            _MESSAGE_TYPE_INFO[key] = _decode(val);
        } catch (err) {
            // No ':' there, must be = msg
            let [key, val] = splitInChar(line, "=");
            key = key.trim();
            val = val.trim();
            _MESSAGE_TYPE_INFO[key] = _MESSAGE_TYPE_INFO[val];
        }
    }
}

buildDecoding();

export class Decoder {
    memo;
    location_memo;

    constructor() {
        this.memo = {};
        this.location_memo = {};
    }

    decode_message_type(message_type, message) {
        var handler;
        handler = _MESSAGE_TYPE_INFO[message_type];
        return handler(this, message);
    }
}

function splitInChar(line: string, char: string) {
    const i = line.indexOf(char);
    if (i > 0) {
        const message_type = line.substring(0, i);
        const message = line.substring(i + 1);
        return [message_type, message];
    }
    return undefined;
}

export function* iter_decoded_log_format(stream: string, decoder: Decoder) {
    var decoded, message, message_type;

    for (let line of stream.split(/\r?\n/)) {
        line = line.trim();

        if (line) {
            try {
                const split = splitInChar(line, " ");
                if (split) {
                    [message_type, message] = split;
                    decoded = decoder.decode_message_type(message_type, message);

                    if (decoded) {
                        const m: IMessage = { "message_type": message_type, "decoded": decoded };
                        yield m;
                    }
                }
            } catch (err) {
                console.log("Unable to decode message: " + line);
                console.log(err);
            }
        }
    }
}

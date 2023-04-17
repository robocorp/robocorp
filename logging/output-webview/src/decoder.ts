// Based on the python decoder example.
// Used: https://extendsclass.com/python-to-javascript.html

import parseISO from "date-fns/parseISO";

export interface IMessage {
    readonly message_type: string;
    readonly decoded: any;
}

function version_decode(decoder, message) {
    return { message };
}

function simple_decode(decoder, message) {
    return JSON.parse(message);
}

function decode_time(decoder, time) {
    const parsedTime = parseISO(time);
    // Note: doing toString() in an utc time (which ends with +00:00)
    // will convert it to the local timezone.
    return { time: parsedTime.toString() };
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

function _decode(message_definiton) {
    const names = [];
    const nameToDecode = new Map();
    for (let s of message_definiton.split(",")) {
        s = s.trim();
        const i = s.indexOf(":");
        let decode = "oid";
        if (i != -1) {
            [s, decode] = s.split(":", 2);
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
            ret[name] = nameToDecode.get(name)(decoder, s);
        }
        // console.log("decoded", ret);
        return ret;
    }
    return _decImpl;
}

const start_run = _decode("name:oid, time_delta_in_seconds:float");

const end_run = _decode("status:oid, time_delta_in_seconds:float");

const start_task = _decode("name:oid, libname:oid, source:oid, lineno:int, time_delta_in_seconds:float");

const end_task = _decode("status:oid, message:oid, time_delta_in_seconds:float");

const start_element = _decode(
    "name:oid, libname:oid, type:oid, doc:oid, source:oid, lineno:int, time_delta_in_seconds:float"
);

const end_element = _decode("status:oid, time_delta_in_seconds:float");

const decode_log = _decode("level:str, message:oid, source:oid, lineno:int, time_delta_in_seconds:float");

const id_decode = _decode("part:int, id:str");

const _MESSAGE_TYPE_INFO = {
    "V": version_decode,
    "ID": id_decode,
    "I": simple_decode,
    "T": decode_time,
    "M": decode_memo,
    "SR": start_run,
    "RR": start_run,
    "ER": end_run,
    "ST": start_task,
    "RT": start_task,
    "ET": end_task,
    "SE": start_element,
    "RE": start_element,
    "EE": end_element,
    "EA": _decode("name:oid, type:oid, value:oid"),
    "L": decode_log,
    "LH": decode_log,
    "TG": _decode("tag:oid"),
    "S": _decode("start_time_delta:float"),
    "STB": _decode("message:oid, time_delta_in_seconds:float"),
    "RTB": _decode("message:oid, time_delta_in_seconds:float"),
    "TBE": _decode("source:oid, lineno:int, method:oid, line_content:oid"),
    "TBV": _decode("name:oid, type:oid, value:oid"),
    "ETB": _decode("time_delta_in_seconds:float"),
};

export class Decoder {
    memo;

    constructor() {
        this.memo = {};
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
            const split = splitInChar(line, " ");
            if (split) {
                [message_type, message] = split;
                decoded = decoder.decode_message_type(message_type, message);

                if (decoded) {
                    const m: IMessage = { "message_type": message_type, "decoded": decoded };
                    yield m;
                }
            }
        }
    }
}

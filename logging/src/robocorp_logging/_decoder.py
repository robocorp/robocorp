import datetime
import json


def _decode_oid(decoder, oid):
    return decoder.memo[oid]


def _decode_float(decoder, msg):
    return float(msg)


def _decode_int(decoder, msg):
    return int(msg)


def _decode_str(decoder, msg):
    return msg


def _decode(message_definition, level_diff=0):
    names = []
    name_to_decode = {}
    for s in message_definition.split(","):
        s = s.strip()
        i = s.find(":")
        decode = "oid"
        if i != -1:
            s, decode = s.split(":", 1)
        names.append(s)
        if decode == "oid":
            name_to_decode[s] = _decode_oid

        elif decode == "int":
            name_to_decode[s] = _decode_int

        elif decode == "float":
            name_to_decode[s] = _decode_float

        elif decode == "str":
            name_to_decode[s] = _decode_str

        else:
            raise RuntimeError(f"Unexpected: {decode}")

    def dec_impl(decoder, message):
        decoder.level += level_diff
        splitted = message.split("|", len(names) - 1)
        ret = {}
        for i, s in enumerate(splitted):
            name = names[i]
            try:
                ret[name] = name_to_decode[name](decoder, s)
            except:
                ret[name] = None
        return ret

    return dec_impl


def decode_time(decoder, time):
    decoder.initial_time = datetime.datetime.fromisoformat(time)
    return {"initial_time": time}


def decode_memo(decoder, message):
    memo_id, memo_value = message.split(":", 1)
    memo_value = json.loads(memo_value)
    decoder.memo[memo_id] = memo_value
    return None


_MESSAGE_TYPE_INFO = {
    "V": lambda _decoder, message: {"version": message},
    "I": lambda _decoder, message: {"info": json.loads(message)},
    "ID": _decode("part:int, id:str"),
    "T": decode_time,
    "M": decode_memo,
    "L": _decode("level:str, message:oid, time_delta_in_seconds:float"),
    "LH": _decode("level:str, message:oid, time_delta_in_seconds:float"),
    "SS": _decode(
        "name:oid, suite_id:oid, suite_source:oid, time_delta_in_seconds:float",
        level_diff=+1,
    ),
    "ES": _decode("status:oid, time_delta_in_seconds:float", level_diff=-1),
    "ST": _decode(
        "name:oid, suite_id:oid, lineno:int, time_delta_in_seconds:float", level_diff=+1
    ),
    "ET": _decode(
        "status:oid, message:oid, time_delta_in_seconds:float", level_diff=-1
    ),
    "SK": _decode(
        "name:oid, libname:oid, keyword_type:oid, doc:oid, source:oid, lineno:int, time_delta_in_seconds:float",
        level_diff=+1,
    ),
    "EK": _decode("status:oid, time_delta_in_seconds:float", level_diff=-1),
    "KA": _decode("argument:oid"),
    "AS": _decode("assign:oid"),
    "TG": _decode("tag:oid"),
    "S": _decode("start_time_delta:float"),
}

_MESSAGE_TYPE_INFO["RS"] = _MESSAGE_TYPE_INFO["SS"]
_MESSAGE_TYPE_INFO["RT"] = _MESSAGE_TYPE_INFO["ST"]
_MESSAGE_TYPE_INFO["RK"] = _MESSAGE_TYPE_INFO["SK"]


class Decoder:
    def __init__(self):
        self.memo = {}
        self.initial_time = None
        self.level = 0

    @property
    def ident(self):
        return "    " * self.level

    def decode_message_type(self, message_type, message):
        handler = _MESSAGE_TYPE_INFO[message_type]
        ret = {"message_type": message_type}
        try:
            r = handler(self, message)
            if not r:
                if message_type == "M":
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


def iter_decoded_log_format(stream):
    decoder = Decoder()
    for line in stream.readlines():
        line = line.strip()
        if line:
            message_type, message = line.split(" ", 1)
            decoded = decoder.decode_message_type(message_type, message)
            if decoded:
                yield decoded

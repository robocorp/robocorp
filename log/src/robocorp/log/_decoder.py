import datetime
import json
from logging import getLogger
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple

from .protocols import IReadLines

# Whenever the decoding changes we should bump up this version.
DOC_VERSION = "0.0.2"

# name, libname, source, docstring, lineno
Location = Tuple[str, str, str, str, int]

_LOGGER = getLogger(__name__)


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
                    try:
                        info = decoder.location_memo[s]
                    except:
                        _LOGGER.critical(f"Could not find memo: {s}")
                        raise
                    ret["name"] = info[0]
                    ret["libname"] = info[1]
                    ret["source"] = info[2]
                    ret["lineno"] = info[4]

                elif dec_func == "loc_and_doc_id":
                    try:
                        info = decoder.location_memo[s]
                    except:
                        _LOGGER.critical(f"Could not find location_memo: {s}")
                        raise
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

_MESSAGE_TYPE_INFO: Dict[str, Callable[[Decoder, str], Any]] = {}


def _build_decoding():
    from robocorp.log._decoder_spec import SPEC

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

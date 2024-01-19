from pathlib import Path
from typing import Optional

from robocorp.log._constants import UNSCOPED_ELEMENTS
from robocorp.log.protocols import IReadLines

_format_msg: dict = {}
_format_msg["SE"] = lambda msg: f"SE: {msg['type']}: {msg['name']}"
_format_msg["YR"] = lambda msg: f"YR: {msg['name']} ({msg['libname']})"
_format_msg["YFR"] = lambda msg: f"YR: {msg['name']} ({msg['libname']})"
_format_msg["EE"] = lambda msg: f"EE: {msg['type']}: {msg['status']}"
_format_msg["YS"] = lambda msg: f"YS: {msg['name']}: {msg['value']} ({msg['libname']})"
_format_msg["YFS"] = lambda msg: f"YS: {msg['name']}: ({msg['libname']})"
_format_msg["EA"] = lambda msg: f"EA: {msg['type']}: {msg['name']}: {msg['value']}"
_format_msg["STB"] = lambda msg: f"STB: {msg['message']}"
_format_msg["AS"] = lambda msg: f"AS: {msg['target']}: {msg['value']}"
_format_msg["ST"] = lambda msg: f"ST: {msg['name']}"
_format_msg["ET"] = lambda msg: f"ET: {msg['status']}"
_format_msg["SR"] = lambda msg: f"SR: {msg['name']}"
_format_msg["ER"] = lambda msg: f"ER: {msg['status']}"

_format_msg["RR"] = lambda msg: f"RR: {msg['name']}"
_format_msg["RT"] = lambda msg: f"RT: {msg['name']}"
_format_msg["RE"] = lambda msg: f"RE: {msg['type']}: {msg['name']}"
_format_msg["R"] = lambda msg: f"R: {msg['type']}: {msg['value']}"


_ignore = {
    "ETB",
    "TBV",
    "TBE",
    "I",
    "T",
    "ID",
    "V",
    "C",
    "STD",
    "ETD",
    "EPS",
    "L",
    "SPS",
}


def pretty_format_logs_from_log_html(log_html: Path, **kwargs):
    from robocorp.log import iter_decoded_log_format_from_log_html

    iter_in = iter_decoded_log_format_from_log_html(log_html)
    return pretty_format_logs_from_iter(iter_in, **kwargs)


def pretty_format_logs_from_log_html_contents(
    log_html_contents: str, log_html: Optional[Path] = None, **kwargs
) -> str:
    from robocorp.log import iter_decoded_log_format_from_log_html_contents

    iter_in = iter_decoded_log_format_from_log_html_contents(
        log_html_contents, log_html
    )
    return pretty_format_logs_from_iter(iter_in, **kwargs)


def pretty_format_logs_from_stream(stream: IReadLines, **kwargs) -> str:
    from robocorp.log import iter_decoded_log_format_from_stream

    iter_in = iter_decoded_log_format_from_stream(stream)
    return pretty_format_logs_from_iter(iter_in, **kwargs)


def add_line(original_lambda):
    def new_func(msg):
        ret = original_lambda(msg)
        try:
            ret += f" (line: {msg['lineno']})"
        except KeyError:
            # Ok, no lineno in msg
            pass
        return ret

    return new_func


def format_log(msg):
    ret = f"L: {msg['level']}: {msg['message']!r}"
    # Fix messages that always change.
    if ret.startswith("L: I: 'System information:\\nMemory:"):
        ret = ret[: len("L: I: 'System information:\\nMemory:")]
    elif ret.startswith("L: I: 'Current Process:"):
        ret = ret[: len("L: I: 'Current Process:")]
    return ret


def pretty_format_logs_from_iter(
    iter_in,
    show_exception_vars=False,
    show_console_messages=False,
    show_log_messages=False,
    show_lines=False,
    show_restarts=True,
) -> str:
    import re

    format_msg = _format_msg.copy()
    ignore = _ignore.copy()
    if show_exception_vars:
        ignore.remove("TBV")
        ignore.remove("TBE")
        format_msg["TBE"] = lambda msg: f"TBE --- {msg['method']} ---"
        format_msg["TBV"] = lambda msg: f"TBV: {msg['name']}: {msg['value']}"

    if show_console_messages:
        ignore.remove("C")
        format_msg["C"] = lambda msg: f"C: {msg['kind']}: {msg['message']!r}"

    if show_log_messages:
        ignore.remove("L")
        format_msg["L"] = format_log

    if show_lines:
        for key in tuple(format_msg.keys()):
            format_msg[key] = add_line(format_msg[key])

    level = 0
    indent = ""
    out = ["\n"]
    regular_start_found = False
    for msg in iter_in:
        msg_type = msg["message_type"]
        if msg_type not in format_msg:
            if msg_type in ignore:
                continue
            print("TODO: Handle: ", msg)
            continue

        # Messages that end scope
        if msg_type in ("EE", "ET", "ER", "YS", "YFS"):
            level -= 1
            indent = "    " * level

        is_restart = msg_type in ("RR", "RT", "RE", "RYR", "RYFR")

        try:
            formatted = format_msg[msg_type](msg)
            pattern = r"at 0x[0-9A-Fa-f]+>"
            formatted = re.sub(pattern, "at 0xXXXXXXXXX>", formatted)
            if (show_restarts and is_restart) or not is_restart:
                out.append(f"{indent}{formatted}\n")
        except Exception:
            raise RuntimeError(f"Error handling message: {msg}")

        # Messages that restart scope
        if is_restart and regular_start_found:
            continue

        if not regular_start_found:
            if msg_type in ("SE", "ST", "SR", "YR", "YFR"):
                regular_start_found = True

        # Messages that create scope
        if msg_type in ("SE", "ST", "SR", "YR", "YFR") or is_restart:
            # Exceptions which won't create scope for SE.
            if msg_type == "SE" and msg["type"] in UNSCOPED_ELEMENTS:
                continue

            level += 1
            indent = "    " * level
    return "".join(out)

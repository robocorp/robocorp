import typing

_convert = {
    "gb": lambda s: s * 1e9,
    "g": lambda s: s * 1e9,
    "mb": lambda s: s * 1e6,
    "m": lambda s: s * 1e6,
    "kb": lambda s: s * 1000,
    "k": lambda s: s * 1000,
    "b": lambda s: s,
    "": lambda s: s,
}


def _convert_to_bytes(s: typing.Union[int, float, str]) -> int:
    if not isinstance(s, str):
        return int(s)

    initial = s
    num_lst = []
    while s and (s[0].isdigit() or s[0] == "."):
        num_lst.append(s[0])
        s = s[1:]
    num = float("".join(num_lst))
    unit = s.strip()
    conv = _convert.get(unit.lower())
    if conv is None:
        raise ValueError(f"Cannot get in bytes: {initial}")

    return int(conv(num))

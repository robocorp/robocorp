import datetime
from dataclasses import dataclass


def callit(arg, date, mydata, bigmultiline, wrapped):
    return


@dataclass
class MyData:
    one: str = "one"
    two: str = "two"


class WrapAStr:
    def __init__(self, s):
        self._str = s

    def __repr__(self):
        return f"WrapStr({self._str})"

    __str__ = __repr__


def check():
    a = list(range(20))
    dct = dict(zip(a, a))
    dct2 = {1: a, "some key": "some value", "another": dct}
    date = {
        "beautiful output": datetime.datetime(
            year=2017, month=12, day=12, hour=0, minute=43, second=4, microsecond=752094
        )
    }
    mydata = MyData()
    bigmultiline = """
This is a big multiline
string.

The text that is in this string
does span across multiple lines.

It should appear well in logs anyways!
"""
    wrapped = WrapAStr(bigmultiline)
    callit(dct2, date, mydata, bigmultiline, wrapped)

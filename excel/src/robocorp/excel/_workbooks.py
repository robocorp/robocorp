import logging
import pathlib
from collections import defaultdict
from contextlib import contextmanager
from io import BytesIO
from typing import Any, List, Optional, Union

import openpyxl
import xlrd
import xlwt
from openpyxl.utils import get_column_letter
from openpyxl.utils.exceptions import InvalidFileException
from xlutils.copy import copy as xlutils_copy

from robocorp.excel._types import PathType
from robocorp.excel._tables import Table
from robocorp.excel._worksheet import Worksheet


def _get_column_index(column: str) -> int:
    """Get column index from name, e.g. A -> 1, D -> 4, AC -> 29.

    Reverse of `get_column_letter()`
    """
    column = str(column).lower()

    col = 0
    for digit, char in enumerate(column[::-1]):
        value = ord(char) - 96
        col += (26**digit) * value

    return col


def _ensure_unique(values: Any) -> List[Any]:
    """Ensures that each string value in the list is unique.

    Adds a suffix to each value that has duplicates,
    e.g. [Banana, Apple, Lemon, Apple] -> [Banana, Apple, Lemon, Apple_2]
    """

    def to_unique(values: Any) -> List[Any]:
        output = []
        seen = defaultdict(int)
        for value in values:
            if seen[value] and isinstance(value, str):
                output.append("%s_%d" % (value, seen[value] + 1))
            else:
                output.append(value)
            seen[value] += 1
        return output

    # Repeat process until each column is unique
    output = to_unique(values)
    while True:
        verify = to_unique(output)
        if output == verify:
            break
        output = verify

    return output

"""
Main module for doing Excel automation.

This library can be made available by pinning
[![`robocorp-excel`](https://img.shields.io/pypi/v/robocorp-excel?label=robocorp-excel)](https://pypi.org/project/robocorp-excel/)
in your dependencies' configuration.
"""

from robocorp.excel.excel import create_workbook, open_workbook
from robocorp.excel.tables import Table

__version__ = "0.4.4"
__all__ = [
    "create_workbook",
    "open_workbook",
    "Table",
]

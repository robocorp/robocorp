from abc import ABC, abstractmethod, abstractproperty


class BaseWorkbook:
    """Common logic for both .xls and .xlsx files management."""

    @abstractproperty
    def sheetnames(self) -> list[str]:
        raise NotImplementedError

    @abstractproperty
    def is_sheet_empty(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def worksheet(self, name: str) -> Worksheet:
        raise NotImplementedError

    @abstractmethod
    def open(self, path, read_only=False, write_only=False, data_only=False):
        raise NotImplementedError

    def active(self):
        raise NotImplementedError

    def save(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError

    def create(self):
        raise NotImplementedError

    def create_worksheet(self):
        raise NotImplementedError

    def extension(self):
        raise NotImplementedError

    def find_empty_row(self):
        raise NotImplementedError

    def read_only(self):
        raise NotImplementedError

    def read_worksheet(self):
        raise NotImplementedError

    def append_worksheet(self):
        raise NotImplementedError

    def rename_worksheet(self):
        raise NotImplementedError

    def remove_worksheet(self):
        raise NotImplementedError

    def set_cell_value(self):
        raise NotImplementedError

    def get_cell_value(self):
        raise NotImplementedError

    def set_cell_format(self):
        raise NotImplementedError

    def insert_image(self):
        raise NotImplementedError

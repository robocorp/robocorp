import copy

from robocorp.workitems._adapters import BaseAdapter
from robocorp.workitems._exceptions import EmptyQueue
from robocorp.workitems._types import State

PAYLOAD_FIRST = {"username": "testguy", "address": "guy@company.com"}
PAYLOAD_SECOND = {"username": "another", "address": "dude@company.com"}

OUTPUT_ID = "workitem-id-out"

MOCK_DATA = {
    "workitem-id-first": PAYLOAD_FIRST,
    "workitem-id-second": PAYLOAD_SECOND,
    OUTPUT_ID: [1, 2, 3],
}
MOCK_FILES = {
    "workitem-id-first": {
        "file1.txt": b"data1",
        "file2.txt": b"data2",
        "file3.png": b"data3",
    },
    "workitem-id-second": {},
    OUTPUT_ID: {},
}


class MockAdapter(BaseAdapter):
    DATA = {}
    FILES = {}
    INDEX = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._data_keys = []
        self.releases = []

    @classmethod
    def reset(cls):
        cls.DATA = copy.deepcopy(MOCK_DATA)
        cls.FILES = copy.deepcopy(MOCK_FILES)
        cls.INDEX = 0

    @classmethod
    def validate(cls, item, key, val):
        data = cls.DATA.get(item.id)
        assert data is not None
        assert data[key] == val

    @property
    def data_keys(self):
        if not self._data_keys:
            self._data_keys = list(self.DATA.keys())
        return self._data_keys

    def reserve_input(self) -> str:
        if self.INDEX >= len(self.data_keys):
            raise EmptyQueue("No work items in the input queue")

        try:
            return self.data_keys[self.INDEX]
        finally:
            self.INDEX += 1

    def release_input(self, item_id: str, state: State, exception=None):
        self.releases.append((item_id, state, exception))  # purely for testing purposes

    def create_output(self, parent_id, payload=None) -> str:
        self.save_payload(OUTPUT_ID, payload)
        return OUTPUT_ID

    def load_payload(self, item_id):
        return self.DATA[item_id]

    def save_payload(self, item_id, payload):
        self.DATA[item_id] = payload

    def list_files(self, item_id):
        return self.FILES[item_id]

    def get_file(self, item_id, name):
        return self.FILES[item_id][name]

    def add_file(self, item_id, name, *, original_name, content):
        self.FILES[item_id][name] = content

    def remove_file(self, item_id, name):
        del self.FILES[item_id][name]

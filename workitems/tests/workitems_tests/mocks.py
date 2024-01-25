import copy

from robocorp.workitems._adapters import BaseAdapter
from robocorp.workitems._exceptions import EmptyQueue
from robocorp.workitems._types import State

PAYLOAD_FIRST = {"username": "testguy", "address": "guy@company.com"}
PAYLOAD_SECOND = {"username": "another", "address": "dude@company.com"}

MOCK_DATA = {
    "workitem-id-first": PAYLOAD_FIRST,
    "workitem-id-second": PAYLOAD_SECOND,
}
MOCK_FILES = {
    "workitem-id-first": {
        "file1.txt": b"data1",
        "file2.txt": b"data2",
        "file3.png": b"data3",
    },
    "workitem-id-second": {},
}


class MockAdapter(BaseAdapter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.index = 0
        self.data = {}
        self.files = {}
        self.releases = []

    def reset(self):
        self.index = 0
        self.data = copy.deepcopy(MOCK_DATA)
        self.files = copy.deepcopy(MOCK_FILES)

    def validate(self, item, key, val):
        data = self.data.get(item.id)
        assert data is not None
        assert data[key] == val

    def reserve_input(self) -> str:
        if self.index >= len(self.data):
            raise EmptyQueue("No work items in the input queue")

        try:
            keys = list(self.data.keys())
            return keys[self.index]
        finally:
            self.index += 1

    def release_input(self, item_id: str, state: State, exception=None):
        self.releases.append((item_id, state, exception))  # purely for testing purposes

    def create_output(self, parent_id, payload=None) -> str:
        output_id = f"{parent_id}-output"
        self.save_payload(output_id, payload)
        self.files[output_id] = {}
        return output_id

    def load_payload(self, item_id):
        return self.data[item_id]

    def save_payload(self, item_id, payload):
        self.data[item_id] = payload

    def list_files(self, item_id):
        return list(self.files[item_id].keys())

    def get_file(self, item_id, name):
        return self.files[item_id][name]

    def add_file(self, item_id, name, content):
        files = self.files.setdefault(item_id, {})
        files[name] = content

    def remove_file(self, item_id, name):
        del self.files[item_id][name]

from typing import Optional

from ._adapters import BaseAdapter, create_adapter
from ._workitem import Input, Output


class Context:
    def __init__(self, adapter: Optional[BaseAdapter] = None) -> None:
        self._inputs: list[Input] = []
        self._adapter: Optional[BaseAdapter] = adapter

    @property
    def inputs(self) -> list[Input]:
        return self._inputs

    @property
    def outputs(self) -> list[Output]:
        items = []
        for item in self._inputs:
            items.extend(item.outputs)
        return items

    @property
    def adapter(self):
        if self._adapter is None:
            self._adapter = create_adapter()

        return self._adapter

    @property
    def current_input(self):
        if not self._inputs:
            return None

        return self._inputs[-1]

    def reserve_input(self) -> Input:
        current = self.current_input
        if current is not None and not current.released:
            raise RuntimeError("Previous input not released")

        item_id = self.adapter.reserve_input()
        item = Input(adapter=self.adapter, item_id=item_id)
        item.load()

        self._inputs.append(item)
        return item

    def create_output(self) -> Output:
        parent = self.current_input
        if parent is None:
            raise RuntimeError("Unable to create output without an input item")

        return parent.create_output()

import os
from typing import Optional, Type, Union

from ._adapters import BaseAdapter, FileAdapter, RobocorpAdapter
from ._utils import import_by_name
from ._workitem import Input, Output


class Context:
    def __init__(
        self,
        default_adapter: Union[Type[BaseAdapter], str] = RobocorpAdapter,
    ):
        self._inputs: list[Input] = []

        # Check RPA_WORKITEMS_ADAPTER for backwards compatibility
        adapter = (
            os.getenv("RC_WORKITEM_ADAPTER")
            or os.getenv("RPA_WORKITEMS_ADAPTER")
            or default_adapter
        )

        self._adapter_class = self._to_adapter_class(adapter)
        self._adapter: Optional[BaseAdapter] = None

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
            self._adapter = self._adapter_class()

        return self._adapter

    @property
    def current_input(self):
        if not self._inputs:
            return None

        return self._inputs[-1]

    def _to_adapter_class(
        self, adapter: Union[Type[BaseAdapter], str]
    ) -> Type[BaseAdapter]:
        if isinstance(adapter, str):
            # Backwards compatibility
            if adapter in ("FileAdapter", "RPA.Robocorp.WorkItems.FileAdapter"):
                adapter = FileAdapter
            else:
                adapter = import_by_name(adapter, __name__)

        if not isinstance(adapter, type) or not issubclass(adapter, BaseAdapter):
            raise ValueError(f"Adapter '{adapter}' does not inherit from BaseAdapter")

        return adapter

    def reserve_input(self) -> Input:
        current = self.current_input
        if current is not None and not current.released:
            raise RuntimeError("Previous input not released")

        item_id = self.adapter.reserve_input()
        item = Input(item_id=item_id, adapter=self.adapter)
        self._inputs.append(item)

        return item

    def create_output(self) -> Output:
        parent = self.current_input
        if parent is None:
            raise RuntimeError("Unable to create output without an input item")

        return parent.create_output()

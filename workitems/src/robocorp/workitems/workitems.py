from typing import List, Optional, Union

from robocorp.workitems._workitems._workitems import _WorkItemsSingleton
from robocorp.workitems.workitem import WorkItem


class _WorkItemsInputs:
    @staticmethod
    def iterate(items_limit: int = 0):
        wi = _WorkItemsSingleton.instance()
        for item in wi.iter_input_work_item(items_limit):
            yield item

    @staticmethod
    def reserve():
        wi = _WorkItemsSingleton.instance()
        return wi.get_input_work_item()

    @property
    def current(self) -> WorkItem:
        wi = _WorkItemsSingleton.instance()
        return wi.current


class _WorkItemsOutputs:
    @staticmethod
    def create(
        variables: Optional[dict] = None,
        files: Optional[Union[str, List[str]]] = None,
        save: bool = True,
    ) -> WorkItem:
        wi = _WorkItemsSingleton.instance()
        return wi.create_output_work_item(variables, files, save)

    @staticmethod
    def show():
        wi = _WorkItemsSingleton.instance()
        return wi.outputs.copy()


inputs = _WorkItemsInputs()
outputs = _WorkItemsOutputs()

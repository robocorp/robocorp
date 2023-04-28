from typing import Any, Callable, Generator, List, Optional, Union

from robocorp.workitems._workitems._workitems import _WorkItemsSingleton
from robocorp.workitems.workitem import Error, State, WorkItem


def get_next_input() -> WorkItem:
    wi = _WorkItemsSingleton.instance()
    return wi.get_input_work_item()


def get_inputs() -> List[WorkItem]:
    return _WorkItemsSingleton.instance().inputs


def get_outputs() -> List[WorkItem]:
    return _WorkItemsSingleton.instance().outputs


def iter_input_work_items(items_limit=0) -> Generator[WorkItem, None, None]:
    wi = _WorkItemsSingleton.instance()
    for item in wi.iter_input_work_item(items_limit):
        yield item


def for_each_input_work_item(
    func: Union[str, Callable],
    *args,
    items_limit: int = 0,
    return_results: bool = True,
    **kwargs,
) -> List[Any]:
    wi = _WorkItemsSingleton.instance()
    return wi.for_each_input_work_item(
        func, *args, items_limit, return_results, **kwargs
    )


def create_output_work_item(
    variables: Optional[dict] = None,
    files: Optional[Union[str, List[str]]] = None,
    save: bool = False,
    parent: WorkItem = None,
) -> WorkItem:
    wi = _WorkItemsSingleton.instance()
    return wi.create_output_work_item(variables, files, save, parent)


def release_input_work_item(
    state: Union[State, str],
    exception_type: Optional[Union[Error, str]] = None,
    code: Optional[str] = None,
    message: Optional[str] = None,
    _auto_release: bool = False,
):
    wi = _WorkItemsSingleton.instance()
    wi.release_input_work_item(state, exception_type, code, message, _auto_release)


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

    @staticmethod
    def create_output(
        variables: Optional[dict] = None,
        files: Optional[Union[str, List[str]]] = None,
        save: bool = False,
    ):
        wi = _WorkItemsSingleton.instance()
        return wi.create_output_work_item(variables, files, save, wi.current)


class _WorkItemsOutputs:
    @staticmethod
    def create(
        variables: Optional[dict] = None,
        files: Optional[Union[str, List[str]]] = None,
        save: bool = False,
    ) -> WorkItem:
        wi = _WorkItemsSingleton.instance()
        return wi.create_output_work_item(variables, files, save)

    @staticmethod
    def show():
        wi = _WorkItemsSingleton.instance()
        return wi.outputs.copy()


inputs = _WorkItemsInputs()
outputs = _WorkItemsOutputs()

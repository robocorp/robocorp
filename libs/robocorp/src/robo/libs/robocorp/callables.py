from typing import Any, Callable, Generator, List, Optional, Union

from robo.libs.robocorp._workitems import _WorkItemsContainer
from robo.libs.robocorp.workitem import Error, State, WorkItem


def get_next_input() -> WorkItem:
    wi = _WorkItemsContainer.instance()
    return wi.get_input_work_item()


def get_inputs() -> List[WorkItem]:
    return _WorkItemsContainer.instance().inputs


def get_outputs() -> List[WorkItem]:
    return _WorkItemsContainer.instance().outputs


def iter_input_work_items(items_limit=0) -> Generator[WorkItem, None, None]:
    wi = _WorkItemsContainer.instance()
    for item in wi.iter_input_work_item(items_limit):
        yield item


def for_each_input_work_item(
    func: Union[str, Callable],
    *args,
    items_limit: int = 0,
    return_results: bool = True,
    **kwargs,
) -> List[Any]:
    wi = _WorkItemsContainer.instance()
    return wi.for_each_input_work_item(
        func, *args, items_limit, return_results, **kwargs
    )


def create_output_work_item(
    variables: Optional[dict] = None,
    files: Optional[Union[str, List[str]]] = None,
    save: bool = False,
) -> WorkItem:
    wi = _WorkItemsContainer.instance()
    return wi.create_output_work_item(variables, files, save)


def release_input_work_item(
    state: Union[State, str],
    exception_type: Optional[Union[Error, str]] = None,
    code: Optional[str] = None,
    message: Optional[str] = None,
    _auto_release: bool = False,
):
    wi = _WorkItemsContainer.instance()
    wi.release_input_work_item(state, exception_type, code, message, _auto_release)

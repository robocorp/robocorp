from typing import List

from robocorp.log import DefaultAutoLogConfig, Filter, FilterKind


def test_auto_log_config() -> None:
    filters: List[Filter] = [
        # Filters are matched in fnmatch style.
        Filter("RPA.*", kind=FilterKind.log_on_project_call),
        Filter("*RPA*", kind=FilterKind.exclude),
        # Just the name actually means matching something as:
        # another|another\.(.*)
        Filter("another", kind=FilterKind.log_on_project_call),
    ]
    config = DefaultAutoLogConfig(filters)
    assert (
        config.get_filter_kind_by_module_name("RPA.bar")
        == FilterKind.log_on_project_call
    )

    assert config.get_filter_kind_by_module_name("myRPA.bar") == FilterKind.exclude
    assert config.get_filter_kind_by_module_name("anothermodule") is None
    assert (
        config.get_filter_kind_by_module_name("another.module")
        == FilterKind.log_on_project_call
    )


def test_auto_log_config_catch_all() -> None:
    filters: List[Filter] = [
        # Filters are matched in fnmatch style.
        Filter("RPA", kind=FilterKind.log_on_project_call),
        Filter("*", kind=FilterKind.full_log),
    ]
    config = DefaultAutoLogConfig(filters)
    assert (
        config.get_filter_kind_by_module_name("RPA.bar")
        == FilterKind.log_on_project_call
    )
    assert config.get_filter_kind_by_module_name("another") == FilterKind.full_log

    # robocorp.log is always excluded.
    assert config.get_filter_kind_by_module_name("robocorp.log") == FilterKind.exclude

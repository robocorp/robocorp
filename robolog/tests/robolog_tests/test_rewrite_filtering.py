def test_rewrite_filtering() -> None:
    import threading
    import email
    from robocorp.robolog import FilterKind, ConfigFilesFiltering, Filter

    # By default accept what's not in the library.
    files_filtering = ConfigFilesFiltering()
    assert (
        files_filtering.get_filter_kind_by_module_name_and_path(__name__, __file__)
        == FilterKind.full_log
    )

    assert (
        files_filtering.get_filter_kind_by_module_name_and_path(
            threading.__name__, threading.__file__
        )
        == FilterKind.exclude
    )
    assert (
        files_filtering.get_filter_kind_by_module_name_and_path(
            email.__name__, email.__file__
        )
        == FilterKind.exclude
    )

    files_filtering = ConfigFilesFiltering(
        filters=[Filter(threading.__name__, FilterKind.log_on_project_call)]
    )
    assert (
        files_filtering.get_filter_kind_by_module_name_and_path(__name__, __file__)
        == FilterKind.full_log
    )
    assert (
        files_filtering.get_filter_kind_by_module_name_and_path(
            threading.__name__, threading.__file__
        )
        == FilterKind.log_on_project_call
    )
    assert (
        files_filtering.get_filter_kind_by_module_name_and_path(
            email.__name__, email.__file__
        )
        == FilterKind.exclude
    )

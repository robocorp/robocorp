def test_rewrite_filtering() -> None:
    from robo_log._rewrite_filtering import FilesFiltering, Filter
    import threading
    import email
    from robo_log import FilterKind

    # By default accept what's not in the library.
    files_filtering = FilesFiltering()
    assert (
        files_filtering.get_modname_or_file_filter_kind(__file__, __name__)
        == FilterKind.full_log
    )

    assert (
        files_filtering.get_modname_or_file_filter_kind(
            threading.__file__, threading.__name__
        )
        == FilterKind.exclude
    )
    assert (
        files_filtering.get_modname_or_file_filter_kind(email.__file__, email.__name__)
        == FilterKind.exclude
    )

    files_filtering = FilesFiltering(
        filters=[Filter(threading.__name__, FilterKind.log_on_project_call)]
    )
    assert (
        files_filtering.get_modname_or_file_filter_kind(__file__, __name__)
        == FilterKind.full_log
    )
    assert (
        files_filtering.get_modname_or_file_filter_kind(
            threading.__file__, threading.__name__
        )
        == FilterKind.log_on_project_call
    )
    assert (
        files_filtering.get_modname_or_file_filter_kind(email.__file__, email.__name__)
        == FilterKind.exclude
    )

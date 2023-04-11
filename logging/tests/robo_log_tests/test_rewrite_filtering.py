def test_rewrite_filtering() -> None:
    from robo_log._rewrite_filtering import FilesFiltering, Filter
    import threading
    import email

    # By default accept what's not in the library.
    files_filtering = FilesFiltering()
    assert files_filtering.accept(__file__, __name__)
    assert not files_filtering.accept(threading.__file__, threading.__name__)
    assert not files_filtering.accept(email.__file__, email.__name__)

    files_filtering = FilesFiltering(
        filters=[Filter(threading.__name__, exclude=False, is_path=False)]
    )
    assert files_filtering.accept(__file__, __name__)
    assert files_filtering.accept(threading.__file__, threading.__name__)
    assert not files_filtering.accept(email.__file__, email.__name__)

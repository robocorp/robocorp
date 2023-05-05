from pathlib import Path


def setup_log_output(
    output_dir: Path,
    max_file_size: str = "1MB",
    max_files: int = 5,
    log_name: str = "log.html",
):
    from robocorp import log

    # This can be called after user code is imported (but still prior to its
    # execution).
    return log.add_log_output(
        output_dir=output_dir,
        max_file_size=max_file_size,
        max_files=max_files,
        log_html=output_dir / log_name,
    )

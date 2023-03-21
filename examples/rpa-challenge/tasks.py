import robocorp_logging
import traceback
from robocorp_logging import Filter

# This needs to be called before importing code which needs to show in the log
# (user or library).
robocorp_logging.setup_auto_logging(
    # TODO: Some bug is preventing this from working.
    # filters=[Filter(name="RPA", exclude=False, is_path=False)]
)


from pathlib import Path

output_dir = Path(__file__).parent / "output"

if __name__ == "__main__":
    # This could be called after user code is imported (but still prior to its
    # execution).
    robocorp_logging.add_log_output(
        output_dir=output_dir,
        max_file_size="1MB",
        max_files=5,
        log_html=output_dir / "log.html",
    )

    # (Optional) Add a way to collect what's being printed in-memory
    # robocorp_logging.add_in_memory_log_output(print).

    status = "PASS"

    try:
        import challenge
    except Exception as e:
        # TODO: Add errors during collection to the logging.
        traceback.print_exc()
        status = "ERROR"

    else:
        robocorp_logging.log_start_suite("challenge", "challenge", challenge.__file__)
        robocorp_logging.log_start_task(
            "run", "challenge.run", challenge.run.__code__.co_firstlineno, []
        )
        try:
            challenge.run()
        except:
            status = "ERROR"
            # TODO: Check if the auto-logging does the right thing here.
            traceback.print_exc()
    finally:
        robocorp_logging.log_end_task("run", "challenge.run", status, "")
        robocorp_logging.log_end_suite("challenge", "challenge", status)
        robocorp_logging.close_log_outputs()

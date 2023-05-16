from robocorp.tasks import task
from robocorp.browser import open_url
from pathlib import Path
import json
from typing import Sequence
import sys


def open_output_view_for_tests():
    filepath = Path(__file__).absolute().parent.parent / "dist-test_v3" / "index.html"
    if not filepath.exists():
        raise AssertionError(
            f'File "{filepath}" does not exist (distribution does not seem to be built with "nmp run build:test").'
        )

    page = open_url(filepath.as_uri(), headless="pydevd" not in sys.modules)
    return page


def compare_strlist(lines_obtained, lines_expected):
    if lines_obtained != lines_expected:
        from itertools import zip_longest

        max_line_length = max(
            len(line) for line in lines_obtained + lines_expected + ["=== Obtained ==="]
        )
        from io import StringIO

        stream = StringIO()

        status = "   "
        print(
            status
            + "{:<{width}}\t{:<{width}}".format(
                "=== Obtained ===", "=== Expected ===", width=max_line_length
            ),
            file=stream,
        )
        for line1, line2 in zip_longest(lines_obtained, lines_expected, fillvalue=""):
            if line1 != line2:
                status = "!! "
            else:
                status = "   "
            print(
                status
                + "{:<{width}}\t{:<{width}}".format(
                    line1, line2, width=max_line_length
                ),
                file=stream,
            )
        obtained = "\n".join(lines_obtained)
        raise AssertionError(
            f"Strings don't match. Obtained:\n\n{obtained}\n\nComparison:\n{stream.getvalue()}"
        )


def check_labels(page, expected_labels: Sequence[str]):
    found = set(s.text_content() for s in page.query_selector_all(".label"))
    assert found == set(expected_labels)


def setup_scenario(page, case_name: str) -> None:
    case_path: Path = (
        Path(__file__).absolute().parent.parent.parent
        / "tests"
        / "robocorp_log_tests"
        / "test_view_integrated_react"
        / (case_name + ".txt")
    )
    contents = case_path.read_text()
    contents_as_json = json.dumps(contents)
    page.evaluate(
        f"""()=>{{
            window['setupScenario']({contents_as_json});
        }}"""
    )


def check_text_from_tree_items(page, expected: Sequence[str]):
    summary_names = [s.text_content() for s in page.query_selector_all(".summaryName")]
    summary_inputs = [
        s.text_content() for s in page.query_selector_all(".summaryInput")
    ]
    found = []
    for name, el_input in zip(summary_names, summary_inputs):
        found.append(f"{name} {el_input}".strip())

    compare_strlist(found, expected)


@task
def case_task_and_element():
    """
    Checks whether the output view works as expected for us.

    Note: the test scenario is actually at:

    /log/tests/robocorp_log_tests/test_view_integrated_react
    """
    page = open_output_view_for_tests()
    page.wait_for_selector("#base-header")  # Check that the page header was loaded

    setup_scenario(page, "case_task_and_element")

    root_text_content = page.locator("#root0 > .entryName").text_content()
    assert root_text_content == "Simple Task"

    toggle_expand = page.locator("#root0 > .toggleExpand")
    toggle_expand.click()

    root_text_content = page.locator("#root0-1 > .entryName").text_content()
    assert root_text_content == "some_method"

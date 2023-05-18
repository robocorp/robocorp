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
        Path(__file__).absolute().parent.parent.parent.parent
        / "tasks"
        / "tests"
        / "tasks_tests"
        / "test_create_scenarios"
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
def case_failure():
    """
    Checks whether the output view works as expected for us.

    Note: the test scenario is actually at:

    /log/tests/robocorp_log_tests/test_view_integrated_react
    """
    page = open_output_view_for_tests()
    page.wait_for_selector("#base-header")  # Check that the page header was loaded

    setup_scenario(page, "case_failure")

    root_text_content = page.query_selector("#root0 > .entryName").text_content()
    assert root_text_content == "Collect tasks"

    root_text_content = page.query_selector("#root1 > .entryName").text_content()
    assert root_text_content == "case_failure"

    # Expand "case_failure"
    assert (
        page.query_selector("#root1-0-0") is not None
    ), "Expected exception to be expanded by default."


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

    # Check for "Simple Task"
    root_text_content = page.locator("#root0 > .entryName").text_content()
    assert root_text_content == "Simple Task"

    # Expand "Simple Task"
    page.locator("#root0 > .toggleExpand").click()

    # Check "some_method"
    some_method_text = page.locator("#root0-0 > .entryName").text_content()
    assert some_method_text == "some_method"

    # Expand "some_method"
    page.locator("#root0-0 > .toggleExpand").click()

    # Check "call_another_method"
    call_another_text = page.locator("#root0-0-0 > .entryName").text_content()
    assert call_another_text == "call_another_method"

    call_another_text = page.locator("#root0-0-0 > .entryValue").text_content()
    assert (
        call_another_text
        == "param0=1, param1='arg', args=(['a', 'b'],), kwargs={'c': 3}"
    )

    # Check that the last method is a leaf and doesn't have the expand button.
    assert page.query_selector("#root0-0-0 > .toggleExpand") is None
    assert page.query_selector("#root0-0-0 > .noExpand") is not None

    # ~ is sibling (columns are as siblings and not inside the item).
    col_location_text = page.locator("#root0-0-0 ~ .colLocation").text_content()
    assert col_location_text == "check:7"

    # ~ is sibling (columns are as siblings and not inside the item).
    col_duration_text = page.locator("#root0-0-0 ~ .colDuration").text_content()
    assert col_duration_text == "0.0 s"

    # Check that the header (run info) is properly set.
    run_badge_text = (
        page.query_selector("#base-header").query_selector(".badge").text_content()
    )
    assert run_badge_text == "Run Passed"

    header_text = (
        page.query_selector("#base-header").query_selector("h1").text_content()
    )
    assert header_text == "Robot1"

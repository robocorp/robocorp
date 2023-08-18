# ruff: noqa: E501
import json
import sys
from pathlib import Path
from typing import Sequence

from robocorp import browser
from robocorp.tasks import task

repo_root = Path(__file__).absolute().parent.parent.parent.parent.parent


def open_output_view_for_tests():
    log_root = repo_root / "log"
    assert log_root.exists(), f"{log_root} does not exist."
    filepath = log_root / "output-react" / "dist-test_v3" / "index.html"
    if not filepath.exists():
        raise AssertionError(
            f'File "{filepath}" does not exist (distribution does not seem '
            'to be built with "npm run build:tests").'
        )

    # Note: set a big viewport height so that the virtual tree shows
    # all the elements we expect.
    browser.configure(headless="pydevd" not in sys.modules, viewport_size=(1024, 2000))
    page = browser.goto(filepath.as_uri())

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
            "Strings don't match. Obtained:\n\n"
            f"{obtained}\n\nComparison:\n{stream.getvalue()}"
        )


def check_labels(page, expected_labels: Sequence[str]):
    found = set(s.text_content() for s in page.query_selector_all(".label"))
    assert found == set(expected_labels)


def setup_scenario(page, case_name: str) -> None:
    case_path: Path = (
        repo_root
        / "integration_tests"
        / "tests"
        / "integration_tests"
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

    runStatus = page.query_selector("#runStatusBadge").text_content()
    assert runStatus == "Run Failed"

    # Expand "case_failure"
    assert (
        page.query_selector("#root1-0-0") is not None
    ), "Expected exception to be expanded by default."


def collect_full_tree_contents(
    parent_id="", has_filter=False, force_name_and_value=False, expand_tree=True
):
    found = {}
    page = browser.page()
    for i in range(100):
        if parent_id:
            entry_id = f"{parent_id}-{i}"
        else:
            entry_id = f"#root{i}"
            if expand_tree:
                # If this is the root, let's expand it recursively.
                toggle_expand = page.query_selector(f"{entry_id} > .toggleExpand")
                if toggle_expand:
                    page.hover(f"{entry_id} > .entryName")
                    page.wait_for_selector(".expandButton")
                    page.query_selector(".expandButton").click()

        element_name = page.query_selector(f"{entry_id} > .entryName")
        element_value = page.query_selector(f"{entry_id} > .entryValue")

        if element_name is not None or element_value is not None:
            if element_name is None:
                text = element_value.text_content()
            else:
                text = element_name.text_content()
                if force_name_and_value:
                    if element_value is not None:
                        if text:
                            text += " - " + element_value.text_content()
                        else:
                            text = element_value.text_content()

            if not text.strip():
                text = (element_name or element_value).evaluate(
                    "(element) => element.tagName"
                )
            found[entry_id] = text

        else:
            if has_filter:
                continue
            return found

        toggle_expand = page.query_selector(f"{entry_id} > .toggleExpand")
        if toggle_expand:
            # toggle_expand.click()
            found.update(
                collect_full_tree_contents(
                    entry_id, has_filter, force_name_and_value, expand_tree=False
                )
            )

    if not has_filter:
        raise AssertionError("Not expecting that many elements...")
    return found


@task
def case_generators():
    """
    Checks whether the output view works as expected for us.

    Note: the test scenario is actually at:

    /log/tests/robocorp_log_tests/test_view_integrated_react
    """
    page = open_output_view_for_tests()
    page.wait_for_selector("#base-header")  # Check that the page header was loaded

    setup_scenario(page, "case_generators")

    full_tree_contents = collect_full_tree_contents()

    found = []
    for name, value in full_tree_contents.items():
        found.append(f"{name} {value}".strip())

    expected = """
#root0 Collect tasks
#root1 case_generators
#root1-0 case_generators
#root1-0-0 call_generators (enter generator)
#root1-0-0-0 call_generators (suspend generator)
#root1-0-1 found_var
#root1-0-2 found_var
#root1-0-3 call_generators (resume generator)
#root1-0-3-0 call_generators (suspend generator)
#root1-0-4 found_var
#root1-0-5 call_generators (resume generator)
#root1-0-5-0 call_generators (suspend generator)
#root1-0-6 found_var
#root1-0-7 call_generators (resume generator)
#root1-0-8 check_ctx_manager (enter generator)
#root1-0-8-0 check_ctx_manager (suspend generator)
#root1-0-9 check_ctx_manager (resume generator)
#root1-0-10 call_generators_in_library (generator lifecycle untracked)
#root1-0-11 found_var
#root1-0-12 found_var
#root1-0-13 found_var                                                                                                                           
#root1-0-14 found_var                                                                                                                           
#root2 Teardown tasks    
"""
    compare_strlist(
        found, [x.strip() for x in expected.splitlines(keepends=False) if x.strip()]
    )


@task
def case_log():
    """
    Checks whether the output view works as expected for us.

    Note: the test scenario is actually at:

    /log/tests/robocorp_log_tests/test_view_integrated_react
    """
    page = open_output_view_for_tests()
    page.wait_for_selector("#base-header")  # Check that the page header was loaded

    setup_scenario(page, "case_log")

    full_tree_contents = collect_full_tree_contents()

    found = []
    for name, value in full_tree_contents.items():
        found.append(f"{name} {value}".strip())

    expected = """
#root0 Collect tasks
#root1 case_log
#root1-0 case_log
#root1-0-0 add_log_in_method
#root1-0-0-0 Some info message
#root1-0-0-1 Some warn message
#root1-0-0-2 Some critical message
#root1-0-1 add_html_log_in_method
#root1-0-1-0 DIV
#root1-0-1-1 DIV
#root1-0-1-2 DIV
#root1-0-2 print_in_another
#root1-0-2-0 Some message in stdout
#root1-0-2-1 Some message in stderr                                       
#root2 Teardown tasks
"""
    compare_strlist(
        found, [x.strip() for x in expected.splitlines(keepends=False) if x.strip()]
    )


@task
def case_search():
    """
    Checks whether the output view works as expected for us.

    Note: the test scenario is actually at:

    /log/tests/robocorp_log_tests/test_view_integrated_react
    """
    page = open_output_view_for_tests()
    page.wait_for_selector("#base-header")  # Check that the page header was loaded

    setup_scenario(page, "case_log")

    locator = page.get_by_placeholder("Search logs")
    locator.type("some")

    # Note: we're not expanding the tree because we want to know what was auto-expanded
    # (so, we only want what's already visible as the search will auto-expand
    # up to the first match).
    full_tree_contents = collect_full_tree_contents(expand_tree=False)

    found = []
    for name, value in full_tree_contents.items():
        found.append(f"{name} {value}".strip())

    expected = """
#root0 Collect tasks
#root1 case_log
#root1-0 case_log
#root1-0-0 add_log_in_method
#root1-0-0-0 Some info message
#root1-0-0-1 Some warn message
#root1-0-0-2 Some critical message
#root1-0-1 add_html_log_in_method
#root1-0-2 print_in_another
#root2 Teardown tasks
"""
    compare_strlist(
        found, [x.strip() for x in expected.splitlines(keepends=False) if x.strip()]
    )

    # Check tha the first message was selected.
    selected_text = page.locator(".selection-visible-light").text_content()
    assert selected_text == "  INFOSome info messagetasks:48"


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


@task
def case_big_structures():
    page = open_output_view_for_tests()
    page.wait_for_selector("#base-header")  # Check that the page header was loaded

    setup_scenario(page, "case_big_structures")

    root_text_content = page.locator("#root0 > .entryName").text_content()
    assert root_text_content == "Simple Task"

    full_tree_contents = collect_full_tree_contents(force_name_and_value=True)

    found = []
    for name, value in full_tree_contents.items():
        found.append(f"{name} {value}".strip())

    expected = r"""
#root0 Simple Task -
#root0-0 check -
#root0-0-0 a - [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19] (list)
#root0-0-1 dct - {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12, 13: 13, 14: 14, 15: 15, 16: 16, 17: 17, 18: 18, 19: 19} (dict)
#root0-0-2 dct2 - {1: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19], 'some key': 'some value', 'another': {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12, 13: 13, 14: 14, 15: 15, 16: 16, 17: 17, 18: 18, 19: 19}} (dict)
#root0-0-3 date - {'beautiful output': datetime.datetime(2017, 12, 12, 0, 43, 4, 752094)} (dict)
#root0-0-4 mydata - MyData(one='one', two='two') (MyData)
#root0-0-5 bigmultiline - '\nThis is a big multiline\nstring.\n\nThe text that is in this string\ndoes span across multiple lines.\n\nIt should appear well in logs anyways!\n' (str)
#root0-0-6 WrapAStr.__init__ - s='\nThis is a big multiline\nstring.\n\nThe text that is in this string\ndoes span across multiple lines.\n\nIt should appear well in logs anyways!\n'
#root0-0-7 wrapped - WrapStr(\nThis is a big multiline\nstring.\n\nThe text that is in this string\ndoes span across multiple lines.\n\nIt should appear well in logs anyways!\n) (WrapAStr)
#root0-0-8 callit - arg={1: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19], 'some key': 'some value', 'another': {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12, 13: 13, 14: 14, 15: 15, 16: 16, 17: 17, 18: 18, 19: 19}}, date={'beautiful output': datetime.da..."""
    compare_strlist(
        found, [x.strip() for x in expected.splitlines(keepends=False) if x.strip()]
    )

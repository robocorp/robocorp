from robocorp.tasks import task
from robocorp.browser import open_url
from pathlib import Path
import json
from typing import Sequence


def open_output_view_for_tests():
    filepath = Path(__file__).absolute().parent.parent / "dist-test_v2" / "index.html"
    if not filepath.exists():
        raise AssertionError(
            f'File "{filepath}" does not exist (distribution does not seem to be built with "yarn build test").'
        )

    page = open_url(filepath.as_uri(), headless=True)
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
    case_path: Path = Path(__file__).absolute().parent / "_resources" / case_name
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


def check_case1(page) -> None:
    setup_scenario(page, "case1.robolog")
    check_labels(page, ["Run Passed", "PASS"])
    check_text_from_tree_items(page, ["Robot1.Simple Task"])


@task
def check_output_webview():
    """
    Checks whether the output view works as expected for us.
    """
    page = open_output_view_for_tests()
    check_case1(page)

    # page.pause()  # Run this to enter in record mode.
    # print("here")

    # page.locator('el_input[name="vBoUw"]').click()
    # page.locator('[id="\\36 IRTq"]').click()
    # page.locator('el_input[name="ZsRnT"]').click()

    # download("http://rpachallenge.com/assets/downloadFiles/challenge.xlsx")
    # people = read_people_from_excel()
    #
    # page.click("button:text('Start')")
    # for person in people:
    #     fill_and_submit_form(page, person)
    #
    # element = page.query_selector("css=div.congratulations")
    # element.screenshot(path=Path("output", "screenshot.png"))

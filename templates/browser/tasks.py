import re
from functools import cache

from robocorp import browser, excel, http
from robocorp.tasks import hooks, task


@hooks.setup
def configure_browser(tasks):
    browser.configure(
        browser_engine="chromium",
        screenshot="only-on-failure",
        headless=False,
    )


@task
def solve_challenge() -> int:
    """Solve the RPA challenge"""
    page = browser.goto("https://rpachallenge.com/")
    page.click("button:text('Start')")

    for row in get_worksheet().as_table(header=True):
        fill_and_submit_form(row)

    duration = get_duration()
    return duration


@cache
def get_worksheet():
    http.download(
        "https://rpachallenge.com/assets/downloadFiles/challenge.xlsx", overwrite=True
    )
    worksheet = excel.open_workbook("challenge.xlsx").worksheet("Sheet1")
    return worksheet


def fill_and_submit_form(row):
    page = browser.page()
    page.fill("//input[@ng-reflect-name='labelFirstName']", str(row["First Name"]))
    page.fill("//input[@ng-reflect-name='labelLastName']", str(row["Last Name"]))
    page.fill("//input[@ng-reflect-name='labelCompanyName']", str(row["Company Name"]))
    page.fill("//input[@ng-reflect-name='labelRole']", str(row["Role in Company"]))
    page.fill("//input[@ng-reflect-name='labelAddress']", str(row["Address"]))
    page.fill("//input[@ng-reflect-name='labelEmail']", str(row["Email"]))
    page.fill("//input[@ng-reflect-name='labelPhone']", str(row["Phone Number"]))
    page.click("input:text('Submit')")


def get_duration():
    page = browser.page()
    result = page.locator("css=.congratulations").inner_text()

    match = re.search(r"(\d+) milliseconds", result)
    assert match is not None, result

    duration = int(match.group(1))
    return duration

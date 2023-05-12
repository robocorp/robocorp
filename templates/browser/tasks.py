from pathlib import Path
from time import sleep

from robocorp import browser, excel, http
from robocorp.tasks import task


@task
def solve_challenge():
    """Solve the RPA challenge"""
    page = browser.open_url("http://rpachallenge.com/", headless=False)

    http.download("http://rpachallenge.com/assets/downloadFiles/challenge.xlsx")
    rows = excel.open_workbook("challenge.xlsx").worksheet("Sheet1").as_table(header=True)

    page.click("button:text('Start')")
    for row in rows:
        fill_and_submit_form(row)

    element = page.locator("css=div.congratulations")
    element.screenshot(path=Path("output", "screenshot.png"))
    sleep(2)


def fill_and_submit_form(row):
    page = browser.page()
    page.fill('//input[@ng-reflect-name="labelFirstName"]', row["First Name"])
    page.fill('//input[@ng-reflect-name="labelLastName"]', row["Last Name"])
    page.fill('//input[@ng-reflect-name="labelCompanyName"]', row["Company Name"])
    page.fill('//input[@ng-reflect-name="labelRole"]', row["Role in Company"])
    page.fill('//input[@ng-reflect-name="labelAddress"]', row["Address"])
    page.fill('//input[@ng-reflect-name="labelEmail"]', row["Email"])
    page.fill('//input[@ng-reflect-name="labelPhone"]', str(row["Phone Number"]))
    page.click("input:text('Submit')")
    sleep(0.5)

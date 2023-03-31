from pathlib import Path
from time import sleep
from playwright.sync_api import Page
from robo.libs.browser import open_url
from robo.libs.http import download
from robo.libs.excel import open_workbook, Table


def read_people_from_excel() -> Table:
    table = open_workbook("challenge.xlsx").worksheet("Sheet1").as_table(header=True)
    print(table)
    return table


def fill_and_submit_form(page: Page, person):
    page.fill('//input[@ng-reflect-name="labelFirstName"]', person["First Name"])
    page.fill('//input[@ng-reflect-name="labelLastName"]', person["Last Name"])
    page.fill('//input[@ng-reflect-name="labelCompanyName"]', person["Company Name"])
    page.fill('//input[@ng-reflect-name="labelRole"]', person["Role in Company"])
    page.fill('//input[@ng-reflect-name="labelAddress"]', person["Address"])
    page.fill('//input[@ng-reflect-name="labelEmail"]', person["Email"])
    page.fill('//input[@ng-reflect-name="labelPhone"]', str(person["Phone Number"]))
    page.click("input:text('Submit')")


def task_solve_challenge():
    page = open_url("http://rpachallenge.com/", headless=False)
    download("http://rpachallenge.com/assets/downloadFiles/challenge.xlsx")
    page.click("button:text('Start')")
    people = read_people_from_excel()
    i = 0
    for person in people:
        i = i + 1
        print(person)
        fill_and_submit_form(page, person)
    print(f"amount of rows inputted {i}")
    # TODO: get the actual path of ARTIFACTS_DIR
    element = page.query_selector("css=div.congratulations")
    element.screenshot(path=Path("output") / "screenshot.png")
    sleep(2)
    # Closing is automatic


if __name__ == "__main__":
    task_solve_challenge()

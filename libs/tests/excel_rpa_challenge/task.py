from pathlib import Path
from time import sleep
from playwright.sync_api import Page
from robo.libs.browser import open_url
from robo.libs.excel import open_workbook, Table


def read_people_from_excel() -> Table:
    table = open_workbook("challenge.xlsx").worksheet("Sheet1").as_table(header=True)
    return table


def fill_and_submit_form(page: Page, person):
    page.fill('//input[@ng-reflect-name="labelFirstName"]', person["First Name"])
    page.fill('//input[@ng-reflect-name="labelLastName"]', person["Last Name"])
    page.fill('//input[@ng-reflect-name="labelCompanyName"]', person["Company Name"])
    #     Input Text    alias:Company Name    ${person}[Company Name]
    page.fill('//input[@ng-reflect-name="labelRole"]', person["Role in Company"])
    #     Input Text    alias:Role in Company    ${person}[Role in Company]
    page.fill('//input[@ng-reflect-name="labelAddress"]', person["Address"])
    #     Input Text    alias:Address    ${person}[Address]
    page.fill('//input[@ng-reflect-name="labelEmail"]', person["Email"])
    page.fill('//input[@ng-reflect-name="labelPhone"]', str(person["Phone Number"]))
    page.click("text=Submit")


def task_solve_challenge():
    page = open_url("http://rpachallenge.com/", headless=False)
    #     Download    http://rpachallenge.com/assets/downloadFiles/challenge.xlsx    overwrite=${TRUE}
    page.click("text=Start")
    people = read_people_from_excel()
    for person in people:
        fill_and_submit_form(page, person)
    # TODO: get the actual path of ARTIFACTS_DIR
    element = page.query_selector("css=div.congratulations")
    element.screenshot(path=Path("output") / "screenshot.png")
    sleep(2)
    # Closing is automatic


if __name__ == "__main__":
    task_solve_challenge()

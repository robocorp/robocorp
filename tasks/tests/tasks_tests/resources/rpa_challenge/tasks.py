# type: ignore
from robocorp import browser
from robocorp.excel import open_workbook
from robocorp.http import download

from robocorp.tasks import task


def read_people_from_excel():
    return open_workbook("challenge.xlsx").worksheet("Sheet1").as_table(header=True)


def fill_and_submit_form(page, person):
    page.fill('//input[@ng-reflect-name="labelFirstName"]', person["First Name"])
    page.fill('//input[@ng-reflect-name="labelLastName"]', person["Last Name"])
    page.fill('//input[@ng-reflect-name="labelCompanyName"]', person["Company Name"])
    page.fill('//input[@ng-reflect-name="labelRole"]', person["Role in Company"])
    page.fill('//input[@ng-reflect-name="labelAddress"]', person["Address"])
    page.fill('//input[@ng-reflect-name="labelEmail"]', person["Email"])
    page.fill('//input[@ng-reflect-name="labelPhone"]', str(person["Phone Number"]))
    page.click("input:text('Submit')")


@task
def solve_challenge():
    """Solve the RPA challenge"""
    browser.configure(headless=True)
    page = browser.goto("http://rpachallenge.com/")

    download("http://rpachallenge.com/assets/downloadFiles/challenge.xlsx")
    people = read_people_from_excel()

    page.click("button:text('Start')")
    for person in people:
        fill_and_submit_form(page, person)

    element = page.query_selector("css=div.congratulations")
    browser.screenshot(element)

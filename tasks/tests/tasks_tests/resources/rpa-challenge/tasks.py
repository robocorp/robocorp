# type: ignore
from pathlib import Path
from time import sleep

from robocorp.tasks import task
from robocorp.http import download
from robocorp.browser import open_url
from robocorp.excel import open_workbook


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
    sleep(0.5)


@task
def solve_challenge():
    """Solve the RPA challenge"""
    page = open_url("http://rpachallenge.com/", headless=True)

    download("http://rpachallenge.com/assets/downloadFiles/challenge.xlsx")
    people = read_people_from_excel()

    page.click("button:text('Start')")
    for person in people:
        fill_and_submit_form(page, person)

    element = page.query_selector("css=div.congratulations")
    element.screenshot(path=Path("output", "screenshot.png"))
    sleep(2)

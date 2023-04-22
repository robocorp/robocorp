from robocorp.tasks import task

from RPA.Browser.Selenium import Selenium
from RPA.Excel.Files import Files
from RPA.HTTP import HTTP

browser_lib = Selenium()


@task
def complete_rpa_challenge():
    start_the_challenge()
    fill_the_forms()
    collect_the_results()


def get_the_list_of_people_from_the_excel_file():
    excel_lib = Files()
    excel_lib.open_workbook("challenge.xlsx")
    table = excel_lib.read_worksheet_as_table(header=True)
    excel_lib.close_workbook()
    return table


def set_value_by_xpath(xpath, value):
    script = f"document.evaluate('{xpath}',document.body,null,9,null).singleNodeValue.value='{value}';"
    return browser_lib.execute_javascript(script)


def fill_and_submit_the_form(person):
    names_and_keys = {
        "labelFirstName": "First Name",
        "labelLastName": "Last Name",
        "labelCompanyName": "Company Name",
        "labelRole": "Role in Company",
        "labelAddress": "Address",
        "labelEmail": "Email",
        "labelPhone": "Phone Number",
    }
    for name, key in names_and_keys.items():
        set_value_by_xpath(f'//input[@ng-reflect-name="{name}"]', person[key])
    browser_lib.click_button("Submit")


def start_the_challenge():
    browser_lib.open_available_browser("http://rpachallenge.com/")
    HTTP().download(
        "http://rpachallenge.com/assets/downloadFiles/challenge.xlsx", overwrite=True
    )
    browser_lib.click_button("Start")


def iter_people_from_excel():
    for person in get_the_list_of_people_from_the_excel_file():
        yield person


def fill_the_forms():
    for person in iter_people_from_excel():
        fill_and_submit_the_form(person)


def collect_the_results():
    browser_lib.capture_element_screenshot("css:div.congratulations")
    browser_lib.close_all_browsers()

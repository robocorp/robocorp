from robocorp import browser, excel, http
from robocorp.tasks import task


@task
def solve_challenge():
    """Solve the RPA challenge"""

    browser.configure(
        # slowmo=100,  # Can be used to activate slow-motion (in millis)
        browser_engine="chrome",  # Can be chrome or firefox
        screenshot="only-on-failure",
        headless=False,
    )
    page = browser.open_url("http://rpachallenge.com/")

    http.download("http://rpachallenge.com/assets/downloadFiles/challenge.xlsx")
    rows = (
        excel.open_workbook("challenge.xlsx").worksheet("Sheet1").as_table(header=True)
    )

    page.click("button:text('Start')")
    for row in rows:
        fill_and_submit_form(row)

    element = page.locator("css=div.congratulations")

    # Can be used to add a screenshot to the logs. If not given any element
    # would take a screenshot of the full page.
    browser.screenshot(element)


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

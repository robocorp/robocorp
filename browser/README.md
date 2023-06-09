# Robocorp browser library

The `robocorp-browser` library helps in automating browsers by providing 
convenient APIs to manage the lifecycle of playwright objects using `robocorp-tasks`.


The code below reflects the basic usage of the library:


```python
from robocorp import browser
from robocorp.tasks import task
from robocorp import vault


@task
def browser_automate():
    # Configure may be used to set the basic robocorp.browser settings.
    # It must be called prior to calling APIs which create playwright objects.
    browser.configure(
        # Note: screenshot="only-on-failure" is actually the default.
        # If the browser_automate() function finishes with an exception it will
        # make a screenshot and embed it into the logs.
        screenshot="only-on-failure",
        # If headless is not passed, it'll show the browser screen only if a
        # debugger is attached.
        headless=True,
    )

    # browser.goto() may be used as a shortcut to get the current page and
    # go to some url (it may create the browser if still not created).
    browser.goto("https://<target-page.com>")

    login()


def login():
    # APIs in robocorp.browser return the same browser instance, which is
    # automatically closed when the task finishes.
    page = browser.page()

    # robocorp.vault is recommended for managing secrets.
    password = vault.get_secret("default-account")["password"]

    # Use the playwright Browser api as usual.
    page.fill('//input[@ng-reflect-name="password"]', password)
    page.click("input:text('Submit')")
```

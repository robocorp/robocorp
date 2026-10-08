# robocorp library quick reference

Common entry points of the `robocorp` meta package (`robocorp-tasks`, `robocorp-browser`, `robocorp-workitems`, `robocorp-vault`, `robocorp-storage`, `robocorp-log`). Signatures change between releases: when the project pins an older version, or something here doesn't match, check the installed package (for example `rcc task script -- python -c "import robocorp.workitems as w; help(w)"`) or the library docs in [robocorp/robocorp](https://github.com/robocorp/robocorp).

## Tasks (`robocorp.tasks`)

```python
from robocorp.tasks import get_output_dir, setup, task, teardown


@task
def process_orders():
    """Docstring is shown as the task description."""
    output = get_output_dir()  # artifacts directory, e.g. output/
```

- Run: `python -m robocorp.tasks run tasks.py -t process_orders` (this is the `shell:` line in `robot.yaml`; locally, run it through `rcc task run`). `-t` takes the function name.
- An uncaught exception fails the task and makes the runner exit non-zero.
- `@setup` / `@teardown` hooks run around every task; pass `scope="session"` to run once per run.
- The run log is written to the artifacts directory as `log.html`.

## Browser (`robocorp.browser`, Playwright)

```python
from robocorp import browser

browser.configure(headless=True, screenshot="only-on-failure")  # before first use
page = browser.goto("https://example.com")  # returns a Playwright Page
page.get_by_role("button", name="Submit").click()
page.get_by_label("Email").fill("user@example.com")
browser.screenshot(page.locator("#result"))  # embeds in the log
```

- `browser.page()`, `browser.context()`, `browser.browser()` and `browser.playwright()` return the managed Playwright objects; everything after that is the standard Playwright sync API.
- Prefer role, label and text locators plus Playwright's auto-waiting (`expect(...)`, `locator.wait_for()`) over CSS position selectors and `time.sleep`.
- The browser is closed automatically when the task ends; don't call `close()` on the managed objects.
- Don't mix with `RPA.Browser.Selenium` / `RPA.Browser.Playwright` in the same project.

## Work items (`robocorp.workitems`)

```python
from robocorp import workitems
from robocorp.workitems import ExceptionType


@task
def consumer():
    for item in workitems.inputs:  # reserves items one at a time
        try:
            order = item.payload["order_id"]
            path = item.get_file("orders.xlsx")  # downloads an attached file
            ...
            workitems.outputs.create({"order_id": order}, files=[path])
            item.done()
        except KeyError as err:
            item.fail(ExceptionType.BUSINESS, code="MISSING_FIELD", message=str(err))
```

- `BUSINESS` failures mean bad input data that shouldn't be retried; `APPLICATION` (the default) means a technical error that may be retried.
- An item that isn't explicitly failed is marked done when its loop iteration finishes. Handle expected errors per item, so one bad item doesn't stop the whole run.
- `workitems.outputs.create(payload, files=...)` needs a reserved input; it creates input for the next step in the process.
- Locally, items come from `RC_WORKITEM_INPUT_PATH` (see "Local work items and secrets" in SKILL.md).

## Vault (`robocorp.vault`)

```python
from robocorp import vault

secret = vault.get_secret("swaglabs")  # Mapping of key -> value
username, password = secret["username"], secret["password"]
```

- Values are hidden from the log by default. Never print or log them yourself.
- Locally, set `RC_VAULT_SECRET_MANAGER=FileSecrets` and `RC_VAULT_SECRETS_FILE`; with Control Room, the extension or agent supplies the connection.

## Asset storage (`robocorp.storage`)

```python
from robocorp import storage

config = storage.get_json("app-config")
storage.set_text("last-run", "2026-01-01")
storage.get_file("template.xlsx", "output/template.xlsx")
```

- Assets live in Control Room, so there is no local file adapter. Code that uses storage needs Control Room access or a guard for local runs.

## Logging (`robocorp.log`)

```python
from robocorp import log

log.info("Processing", order_id)
log.critical("Unrecoverable state")
with log.suppress():  # hide variables and methods while handling sensitive data
    token = fetch_token()
log.hide_from_output(token)
```

- `robocorp.tasks` sets up auto-logging of the project's own functions; library calls aren't logged in detail.

## RPA Framework (`rpaframework`)

Classic libraries such as `RPA.Excel.Files`, `RPA.PDF`, `RPA.HTTP` and `RPA.Email.ImapSmtp` are Python classes:

```python
from RPA.Excel.Files import Files

excel = Files()
excel.open_workbook(path)
rows = excel.read_worksheet_as_table(header=True)
```

Look up keywords at [rpaframework.org](https://rpaframework.org/). Prefer the `robocorp.*` packages above wherever one covers the same need.

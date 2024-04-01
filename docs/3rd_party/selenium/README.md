# Selenium

Selenium is a browser automation tool with a long history being a well tested and go to solution.
It can also be used to automate legacy browsers such as Internet Explorer.

## Usage

```python
from selenium import webdriver
from selenium.webdriver.common.by import By

with webdriver.Chrome() as driver:
    driver.implicitly_wait(10)
    driver.set_window_size(1024, 768)

    driver.get("https://robotsparebinindustries.com/")
    driver.find_element(By.ID, "username").send_keys("maria")
    driver.find_element(By.NAME, "password").send_keys("thoushallnotpass")
    driver.find_element(By.CSS_SELECTOR, "form > button").click()

    driver.find_element(By.XPATH, '//*[@id="logout"]')

    driver.get_screenshot_as_file("robotsparebin.png")
```

> AI/LLM's are quite good with `Selenium`.  
> 👉 Try asking [ReMark](https://chat.robocorp.com)

###### Various [snippets](snippets)

- [Taking the screenshot after login](snippets/screenshot_after_login.py)

## Links and references

- [PyPI](https://pypi.org/project/selenium/)
- [Documentation](https://www.selenium.dev/documentation/)
- [API reference](https://www.selenium.dev/selenium/docs/api/py/api.html/)

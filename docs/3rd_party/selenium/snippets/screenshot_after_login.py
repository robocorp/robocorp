from selenium import webdriver
from selenium.webdriver.common.by import By


def login_and_take_screenshot():
    with webdriver.Chrome() as driver:
        driver.implicitly_wait(10)
        driver.set_window_size(1024, 768)

        driver.get("https://robotsparebinindustries.com/")
        driver.find_element(By.ID, "username").send_keys("maria")
        driver.find_element(By.NAME, "password").send_keys("thoushallnotpass")
        driver.find_element(By.CSS_SELECTOR, "form > button").click()

        driver.find_element(By.XPATH, '//*[@id="logout"]')

        driver.get_screenshot_as_file("robotsparebin.png")

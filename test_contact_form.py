from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


CONTACT_URL = (
    "http://opencart.abstracta.us/"
    "index.php?route=information/contact"
)

ENQUIRY = (
    "Hello, I would like more information about delivery "
    "options for the Canon EOS 5D. Thank you."
)


@pytest.fixture
def driver():
    browser = webdriver.Chrome()
    browser.maximize_window()
    yield browser
    browser.quit()


@pytest.mark.parametrize(
    "scenario,name,email,expected",
    [
        (
            "scenario_1",
            "Theresa",
            "theresa@example.com",
            "Your enquiry has been successfully sent",
        ),
        (
            "scenario_2",
            "",
            "theresa@example.com",
            "Name must be between 3 and 32 characters",
        ),
        (
            "scenario_3",
            "Theresa",
            "theresa.example.com",
            "E-Mail Address does not appear to be valid",
        ),
    ],
)
def test_contact_form(driver, scenario, name, email, expected):
    wait = WebDriverWait(driver, 20)

    try:
        driver.get(CONTACT_URL)

        name_field = wait.until(
            EC.visibility_of_element_located((By.ID, "input-name"))
        )
        name_field.clear()
        name_field.send_keys(name)

        email_field = driver.find_element(By.ID, "input-email")
        email_field.clear()
        email_field.send_keys(email)

        enquiry_field = driver.find_element(By.ID, "input-enquiry")
        enquiry_field.clear()
        enquiry_field.send_keys(ENQUIRY)

        driver.find_element(
            By.CSS_SELECTOR, "input[type='submit']"
        ).click()

        if scenario == "scenario_1":
            wait.until(EC.url_contains("information/contact/success"))
            content = wait.until(
                EC.visibility_of_element_located((By.ID, "content"))
            )
            assert expected.lower() in content.text.lower(), (
                "The success page opened, but the enquiry "
                "confirmation message was missing."
            )
        else:
            error = wait.until(
                EC.visibility_of_element_located(
                    (
                        By.XPATH,
                        f"//div[contains(@class, 'text-danger')]"
                        f"[contains(., '{expected}')]",
                    )
                )
            )
            assert error.is_displayed()
            assert "information/contact/success" not in driver.current_url

    finally:
        Path("screenshots").mkdir(exist_ok=True)
        driver.save_screenshot(f"screenshots/f15_{scenario}.png")
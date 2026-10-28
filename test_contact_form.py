from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# OpenCart Contact Us page used for these tests.
CONTACT_URL = (
    "http://opencart.abstracta.us/"
    "index.php?route=information/contact"
)

# Valid enquiry text used in all three scenarios.
ENQUIRY = (
    "Hello, I would like more information about delivery "
    "options for the Canon EOS 5D. Thank you."
)


# Open Chrome before each test and close it afterwards.
@pytest.fixture
def driver():
    browser = webdriver.Chrome()
    browser.maximize_window()
    yield browser
    browser.quit()


# Run the contact form test with three different sets of inputs.
@pytest.mark.parametrize(
    "scenario,name,email,expected",
    [
        # Scenario 1: completed form with valid details.
        ("scenario_1","Theresa","theresa@example.com","Your enquiry has been successfully sent",),

        # Scenario 2: leave the name empty.
        ("scenario_2","","theresa@example.com","Name must be between 3 and 32 characters",),

        # Scenario 3: enter an email without the @ symbol.
        ("scenario_3","Theresa","theresa.example.com","E-Mail Address does not appear to be valid",),
    ],
)
def test_contact_form(driver, scenario, name, email, expected):
    wait = WebDriverWait(driver, 20)

    try:
        # Open the Contact Us page.
        driver.get(CONTACT_URL)

        # Clear the name field and enter this scenario's name.
        name_field = wait.until(
            EC.visibility_of_element_located((By.ID, "input-name"))
        )
        name_field.clear()
        name_field.send_keys(name)

        # Clear the email field and enter this scenario's email.
        email_field = driver.find_element(By.ID, "input-email")
        email_field.clear()
        email_field.send_keys(email)

        # Enter the enquiry text.
        enquiry_field = driver.find_element(By.ID, "input-enquiry")
        enquiry_field.clear()
        enquiry_field.send_keys(ENQUIRY)

        # Submit the contact form.
        driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

        if scenario == "scenario_1":
            # Check that the success page opens.
            wait.until(
                EC.url_contains("information/contact/success") )

            # Check that a confirmation message is displayed.
            content = wait.until(
                EC.visibility_of_element_located((By.ID, "content")))
            assert expected.lower() in content.text.lower(), (
                "The success page opened, but the enquiry "
                "confirmation message was missing.")

        else:
            # Check that the correct validation error appears.
            error = wait.until(
                EC.visibility_of_element_located(
                    (
                        By.XPATH,
                        "//div[contains(@class, 'text-danger')]"
                        f"[contains(., '{expected}')]",
                    )
                )
            )
            assert error.is_displayed()

            # Invalid details should not open the success page.
            assert (
                "information/contact/success"
                not in driver.current_url)

    finally:
        # Save a screenshot even if the test encounters an error.
        Path("screenshots").mkdir(exist_ok=True)
        driver.save_screenshot(f"screenshots/f15_{scenario}.png")
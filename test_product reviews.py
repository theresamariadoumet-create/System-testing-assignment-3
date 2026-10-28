from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Camera product page used for the review tests.
PRODUCT_URL = (
    "http://opencart.abstracta.us/"
    "index.php?route=product/product&product_id=30"
)

# Valid review text used in scenarios 1 and 2.
REVIEW = (
    "The product information is clear and helpful. "
    "The images and description explain the camera features."
)


# Open Chrome before each test and close it afterwards.
@pytest.fixture
def driver():
    browser = webdriver.Chrome()
    browser.maximize_window()
    yield browser
    browser.quit()


# Fill in the review form and return the response message.
def submit_review(driver, name, review):
    driver.get(PRODUCT_URL)
    wait = WebDriverWait(driver, 20)

    # Wait for the Reviews tab and open it.
    reviews_tab = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "a[href='#tab-review']")
        )
    )
    reviews_tab.click()

    # Clear the name field and enter this scenario's name.
    name_field = wait.until(
        EC.visibility_of_element_located((By.ID, "input-name"))
    )
    name_field.clear()
    name_field.send_keys(name)

    # Clear the review field and enter this scenario's text.
    review_field = driver.find_element(By.ID, "input-review")
    review_field.clear()
    review_field.send_keys(review)

    # Select a rating of 5.
    driver.find_element(
        By.CSS_SELECTOR, "input[name='rating'][value='5']").click()

    # Click Continue to submit the review.
    driver.find_element(By.ID, "button-review").click()

    # Wait for the success or validation message.
    return wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "#tab-review .alert")
        )
    )


# Run the review test with three different sets of inputs.
@pytest.mark.parametrize(
    "scenario,name,review,expected,alert_type",
    [
        # Scenario 1: completed review with a name and rating.
        ("scenario_1","Theresa",REVIEW, "Thank you for your review", "alert-success",
        ),

        # Scenario 2: missing name with valid review text.
        (
            "scenario_2","", REVIEW,"Review Name must be between 3 and 25 characters","alert-danger",
            ),

        # Scenario 3: valid name with missing review text.
        ("scenario_3","Theresa","","Review Text must be between 25 and 1000 characters","alert-danger",
        ),
    ],
)
def test_product_review(
    driver, scenario, name, review, expected, alert_type
):
    try:
        # Submit the inputs provided for this scenario.
        message = submit_review(driver, name, review)

        # Check that the message has the expected type and text.
        assert alert_type in message.get_attribute("class")
        assert expected in message.text

    finally:
        # Save a screenshot even if the test encounters an error.
        Path("screenshots").mkdir(exist_ok=True)
        driver.save_screenshot(f"screenshots/f14_{scenario}.png")
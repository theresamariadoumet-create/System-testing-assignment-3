from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


PRODUCT_URL = (
    "http://opencart.abstracta.us/"
    "index.php?route=product/product&product_id=30"
)

REVIEW = (
    "The product information is clear and helpful. "
    "The images and description explain the camera features."
)


@pytest.fixture
def driver():
    browser = webdriver.Chrome()
    browser.maximize_window()
    yield browser
    browser.quit()


def submit_review(driver, name, review):
    driver.get(PRODUCT_URL)
    wait = WebDriverWait(driver, 20)

    reviews_tab = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "a[href='#tab-review']")
        )
    )
    reviews_tab.click()

    name_field = wait.until(
        EC.visibility_of_element_located((By.ID, "input-name"))
    )
    name_field.clear()
    name_field.send_keys(name)

    review_field = driver.find_element(By.ID, "input-review")
    review_field.clear()
    review_field.send_keys(review)

    driver.find_element(
        By.CSS_SELECTOR, "input[name='rating'][value='5']"
    ).click()

    driver.find_element(By.ID, "button-review").click()

    return wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "#tab-review .alert")
        )
    )


@pytest.mark.parametrize(
    "scenario,name,review,expected,alert_type",
    [
        (
            "scenario_1",
            "Theresa",
            REVIEW,
            "Thank you for your review",
            "alert-success",
        ),
        (
            "scenario_2",
            "",
            REVIEW,
            "Review Name must be between 3 and 25 characters",
            "alert-danger",
        ),
        (
            "scenario_3",
            "Theresa",
            "",
            "Review Text must be between 25 and 1000 characters",
            "alert-danger",
        ),
    ],
)
def test_product_review(
    driver, scenario, name, review, expected, alert_type
):
    try:
        message = submit_review(driver, name, review)

        assert alert_type in message.get_attribute("class")
        assert expected in message.text
    finally:
        Path("screenshots").mkdir(exist_ok=True)
        driver.save_screenshot(f"screenshots/f14_{scenario}.png")
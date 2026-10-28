from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# OpenCart homepage containing the promotional banners.
HOME_URL = (
    "http://opencart.abstracta.us/"
    "index.php?route=common/home"
)


# Open Chrome before each test and close it afterwards.
@pytest.fixture
def driver():
    browser = webdriver.Chrome()
    browser.maximize_window()
    yield browser
    browser.quit()


# Open the homepage and wait for the banner slideshow.
def open_homepage(driver):
    driver.get(HOME_URL)

    return WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.ID, "slideshow0"))
    )


# Use the slideshow dots to find the iPhone banner.
def find_phone_banner(driver):
    wait = WebDriverWait(driver, 20)
    slideshow = open_homepage(driver)

    bullets = slideshow.find_elements(
        By.CSS_SELECTOR, ".swiper-pagination-bullet"
    )

    for bullet in bullets:
        bullet.click()

        # Find the image in the currently active slide.
        def active_image(browser):
            images = browser.find_elements(
                By.CSS_SELECTOR,
                "#slideshow0 .swiper-slide-active img",
            )

            for image in images:
                if image.is_displayed():
                    return image

            return False

        image = wait.until(active_image)

        # Identify the phone banner using its image information.
        description = (
            (image.get_attribute("alt") or "")
            + " "
            + (image.get_attribute("src") or "")
        ).lower()

        if "iphone" in description:
            return image

    raise AssertionError("The iPhone banner was not found.")


# Save a screenshot as evidence of the test.
def save_evidence(driver, scenario):
    Path("screenshots").mkdir(exist_ok=True)
    driver.save_screenshot(f"screenshots/f18_{scenario}.png")


# Scenario 1: check that the banner image loads and is visible.
def test_banner_display(driver):
    try:
        open_homepage(driver)

        image = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "#slideshow0 .swiper-slide-active img",
                )
            )
        )

        # Check that the browser has loaded the image successfully.
        loaded = WebDriverWait(driver, 20).until(
            lambda browser: browser.execute_script(
                "return arguments[0].complete "
                "&& arguments[0].naturalWidth > 0;",
                image,
            )
        )

        assert loaded
        assert image.size["width"] > 0
        assert image.size["height"] > 0

    finally:
        save_evidence(driver, "scenario_1")


# Scenario 2: check that the phone banner opens an iPhone page.
def test_banner_destination(driver):
    try:
        image = find_phone_banner(driver)
        image.click()

        # Read the heading of the destination page.
        heading = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "#content h1")
            )
        )

        # The product should match the phone shown in the banner.
        assert "iphone" in heading.text.lower(), (
            f"The iPhone banner opened '{heading.text}' "
            "instead of an iPhone product page."
        )

    finally:
        save_evidence(driver, "scenario_2")


# Scenario 3: repeat navigation and compare the destinations.
def test_repeated_banner_navigation(driver):
    destinations = []

    for attempt in range(1, 4):
        try:
            # Return home, find the phone banner and click it.
            image = find_phone_banner(driver)
            image.click()

            # Wait for a product page to open.
            WebDriverWait(driver, 20).until(
                EC.url_contains("route=product/product"))

            WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "#content h1"))
            )

            # Record the destination for this attempt.
            destinations.append(driver.current_url)

        finally:
            save_evidence(
                driver, f"scenario_3_attempt_{attempt}" )

    # Check that all three attempts opened the same destination.
    assert len(destinations) == 3
    assert len(set(destinations)) == 1, ("The banner opened different destinations.")
"""
Environment for Behave testing
"""

from os import getenv
from selenium import webdriver

WAIT_SECONDS = int(getenv("WAIT_SECONDS", "60"))
BASE_URL = getenv("BASE_URL", "http://localhost:8080")


def before_all(context):
    """Executed once before all tests"""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")  # Bypass OS security model
    context.driver = webdriver.Chrome(options=options)
    context.wait_seconds = WAIT_SECONDS
    context.driver.implicitly_wait(context.wait_seconds)
    context.base_url = BASE_URL


def after_all(context):
    """Executed after all tests"""
    if hasattr(context, "driver"):
        context.driver.quit()

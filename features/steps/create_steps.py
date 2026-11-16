"""Steps for creating products through the UI."""

from decimal import Decimal
from uuid import uuid4
from behave import when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def fill_create_field(context, field, value):
    """Fill a Create field."""
    element = context.driver.find_element(By.ID, "create_product_" + field)
    element.clear()
    if value:
        element.send_keys(value)
    context.create_values[field] = value


@when('I fill in a new product with price "{price}"')
def enter_new_product(context, price):
    """Enter a unique product."""
    context.create_values = {}
    for field, value in [("name", "Create-" + uuid4().hex[:12]),
                         ("description", "New product"), ("price", price)]:
        fill_create_field(context, field, value)


@when('I set the new product\'s {field} to "{value}"')
def change_create_field(context, field, value):
    """Change one field."""
    fill_create_field(context, field, {"empty": "", "spaces": "   "}.get(value, value))


@when("I submit the new product")
def submit_new_product(context):
    """Click Create."""
    WebDriverWait(context.driver, context.wait_seconds).until(
        EC.element_to_be_clickable((By.ID, "create-btn"))).click()


@then("I should see the saved product details and generated ID")
def check_created_product(context):
    """Check the server's saved values in the details dialog."""
    WebDriverWait(context.driver, context.wait_seconds).until(
        EC.visibility_of_element_located((By.ID, "retrieve-product-dialog")))
    product_id = context.driver.find_element(By.ID, "detail_product_id").text
    assert int(product_id) > 0
    for field in ("name", "description"):
        assert context.driver.find_element(
            By.ID, "detail_product_" + field).text == context.create_values[field]
    assert Decimal(context.driver.find_element(By.ID, "detail_product_price").text) == Decimal(
        context.create_values["price"])


@then("I should see a product creation success message")
def check_create_success(context):
    """Check the success message."""
    assert context.driver.find_element(By.ID, "flash_message").text == "Product created successfully."


@then('I should see the creation error "{message}"')
def check_create_error(context, message):
    """Check the validation error."""
    WebDriverWait(context.driver, context.wait_seconds).until(
        lambda driver: driver.find_element(By.ID, "create_message").text == message)
    assert "success" not in context.driver.find_element(By.ID, "flash_message").get_attribute("class")


@then("the Create dialog should keep the entered values")
def check_create_values(context):
    """Keep invalid input available for correction."""
    assert context.driver.find_element(By.ID, "create-product-dialog").is_displayed()
    for field, value in context.create_values.items():
        assert context.driver.find_element(
            By.ID, "create_product_" + field).get_attribute("value") == value

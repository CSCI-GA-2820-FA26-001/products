"""Steps for updating products through the UI."""

from decimal import Decimal
from uuid import uuid4
from behave import given, when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def wait(context):
    """Use the shared browser timeout."""
    return WebDriverWait(context.driver, context.wait_seconds)


def click(context, selector):
    """Click a visible enabled control."""
    wait(context).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector))).click()


def fill(context, element_id, value):
    """Type into a visible field."""
    field = wait(context).until(EC.visibility_of_element_located((By.ID, element_id)))
    field.clear()
    field.send_keys(value)


def close_update(context):
    """Close the Update dialog."""
    if context.driver.find_element(By.ID, "update-product-dialog").is_displayed():
        click(context, '#update-product-dialog [data-close]')


@given("an Update test product has been created through the UI")
def create_update_product(context):
    """Create a product for the scenario."""
    context.update_name = "Update-" + uuid4().hex[:12]
    context.updated_name = context.update_name + "-edited"
    context.driver.get(context.base_url)
    click(context, "#open-create-btn")
    for field, value in [("name", context.update_name),
                         ("description", "Original details"), ("price", "19.99")]:
        fill(context, "create_product_" + field, value)
    click(context, "#create-btn")
    wait(context).until(lambda driver: "success" in driver.find_element(
        By.ID, "flash_message").get_attribute("class"))
    context.driver.get(context.base_url)

    def find_row(driver):
        for row in driver.find_elements(By.CSS_SELECTOR, "#products_body tr"):
            if row.find_element(By.CSS_SELECTOR, '[data-action="retrieve"]').text == context.update_name:
                return row
        return False
    row = wait(context).until(find_row)
    context.update_id = row.get_attribute("data-product-id")


@given("I open that product's Update dialog")
def open_update(context):
    """Load the saved product using the row button."""
    click(context, "#update-" + context.update_id)
    wait(context).until(EC.visibility_of_element_located((By.ID, "update-product-dialog")))
    wait(context).until(lambda driver: driver.find_element(
        By.ID, "product_id").get_attribute("value") == context.update_id)


@when("I reopen that product's Update dialog")
def reopen_update(context):
    """Reload and reopen the product."""
    context.driver.get(context.base_url)
    open_update(context)


@when("I enter updated product details")
def edit_product(context):
    """Change all editable product fields."""
    for field, value in [("name", context.updated_name),
                         ("description", "Updated details"), ("price", "24.50")]:
        fill(context, "product_" + field, value)


@when("I enter a negative price in the Update dialog")
def negative_price(context):
    """Enter a negative price."""
    fill(context, "product_price", "-1")


@when("I save the Update dialog")
def save_update(context):
    """Save the changes."""
    click(context, "#update-btn")


@then("the Update dialog reports success")
def success(context):
    """Wait for the successful response message."""
    wait(context).until(lambda driver: driver.find_element(
        By.ID, "update_message").text == "Product updated successfully.")


@then("the Update dialog reports an invalid price")
def invalid_price(context):
    """Check the visible validation message."""
    wait(context).until(lambda driver: "non-negative" in driver.find_element(
        By.ID, "update_message").text)


def assert_fields(context, name, description, price):
    """Check the saved fields including decimal price and original ID."""
    for field, value in [("id", context.update_id), ("name", name),
                         ("description", description)]:
        assert context.driver.find_element(By.ID, "product_" + field).get_attribute("value") == value
    assert Decimal(context.driver.find_element(
        By.ID, "product_price").get_attribute("value")) == Decimal(price)


@then("the updated product details and original ID are displayed")
def updated_fields(context):
    """Check the persisted update."""
    assert_fields(context, context.updated_name, "Updated details", "24.50")


@then("the original product details and ID are displayed")
def original_fields(context):
    """An invalid update must not change the saved values."""
    assert_fields(context, context.update_name, "Original details", "19.99")


@given("I submit a review for the Update test product through the UI")
def submit_review(context):
    """Add a review to the product."""
    close_update(context)
    click(context, "#review-" + context.update_id)
    fill(context, "product_rating", "5")
    fill(context, "product_review_text", "Good quality")
    click(context, "#submit-feedback-btn")
    wait(context).until(lambda driver: "Good quality" in driver.find_element(
        By.ID, "feedback_body").text)
    click(context, '#review-product-dialog [data-close]')


@then("its original review is still displayed through the UI")
def preserved_review(context):
    """Inspect feedback after a fresh page load."""
    context.driver.get(context.base_url)
    click(context, "#review-" + context.update_id)
    wait(context).until(lambda driver: "Good quality" in driver.find_element(
        By.ID, "feedback_body").text)
    rows = context.driver.find_elements(By.CSS_SELECTOR, "#feedback_body tr")
    assert len(rows) == 1
    assert [cell.text for cell in rows[0].find_elements(By.TAG_NAME, "td")] == ["5", "Good quality"]


@given("I delete the Update test product through another browser tab")
def delete_elsewhere(context):
    """Delete the product while its Update dialog stays open."""
    original_tab = context.driver.current_window_handle
    context.driver.switch_to.new_window("tab")
    try:
        context.driver.get(context.base_url)
        click(context, "#delete-" + context.update_id)
        wait(context).until(EC.invisibility_of_element_located(
            (By.ID, "product-" + context.update_id)))
    finally:
        context.driver.close()
        context.driver.switch_to.window(original_tab)


@then("the Update dialog reports that the product was not found")
def missing_product(context):
    """A failed save must not display a success message."""
    wait(context).until(lambda driver: "Product not found" in driver.find_element(
        By.ID, "update_message").text)
    assert "successfully" not in context.driver.find_element(By.ID, "update_message").text


@then("refreshing the page shows that the original product is absent")
def absent_product(context):
    """Check that the product is still absent after reloading."""
    context.driver.get(context.base_url)
    wait(context).until(lambda driver: driver.find_element(
        By.ID, "results_status").get_attribute("data-state") == "ready")
    assert not context.driver.find_elements(By.ID, "product-" + context.update_id)
    assert context.updated_name not in context.driver.find_element(By.ID, "products_body").text

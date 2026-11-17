"""Steps for deleting products through the UI."""

from uuid import uuid4
from behave import given, when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def wait_until(context, condition):
    """Wait for a browser condition."""
    return WebDriverWait(context.driver, context.wait_seconds).until(condition)


def click(context, element_id):
    """Click a visible and enabled control."""
    wait_until(context, EC.element_to_be_clickable((By.ID, element_id))).click()


def create_product(context, role):
    """Create a unique product with the Create dialog and show it in the table."""
    click(context, "open-create-btn")
    for field, value in [
        ("name", f"Delete-{role}-{uuid4().hex[:8]}"),
        ("description", f"Delete test product ({role})"),
        ("price", "5.00"),
    ]:
        element = wait_until(
            context,
            EC.visibility_of_element_located((By.ID, "create_product_" + field)),
        )
        element.clear()
        element.send_keys(value)
    click(context, "create-btn")
    wait_until(
        context, EC.visibility_of_element_located((By.ID, "retrieve-product-dialog"))
    )
    product_id = context.driver.find_element(By.ID, "detail_product_id").text.strip()
    context.driver.find_element(
        By.CSS_SELECTOR, "#retrieve-product-dialog [data-close]"
    ).click()
    click(context, "reset-search-btn")
    wait_until(
        context, EC.visibility_of_element_located((By.ID, "product-" + product_id))
    )
    return product_id


@given("a product exists in the catalog")
def create_target_product(context):
    """Create the product that will be deleted."""
    context.delete_id = create_product(context, "target")


@given("another product exists in the catalog")
def create_kept_product(context):
    """Create a product that should survive the delete, then remove it after the scenario."""
    context.keep_id = create_product(context, "kept")
    context.add_cleanup(click, context, "delete-" + context.keep_id)


@given("the product was already deleted in another window")
def delete_in_another_window(context):
    """Delete the product in a second tab, leaving a stale row in the first."""
    original = context.driver.current_window_handle
    context.driver.switch_to.new_window("tab")
    context.driver.get(context.base_url)
    click(context, "delete-" + context.delete_id)
    wait_until(
        context,
        EC.invisibility_of_element_located((By.ID, "product-" + context.delete_id)),
    )
    context.driver.close()
    context.driver.switch_to.window(original)


@when("I delete the product")
def delete_product(context):
    """Click the row's Delete button."""
    click(context, "delete-" + context.delete_id)


@then("I should see a product deletion success message")
def check_delete_success(context):
    """Check the success message."""
    wait_until(
        context,
        lambda driver: driver.find_element(By.ID, "flash_message").text
        == "Product deleted successfully.",
    )


def wait_for_catalog(context):
    """Wait until the product list has finished loading."""
    wait_until(
        context,
        lambda driver: driver.find_element(By.ID, "results_status").get_attribute(
            "data-state"
        )
        == "ready",
    )


@then("the product should no longer appear in the catalog")
def check_product_removed(context):
    """Check the deleted row is gone after the list reloads."""
    wait_for_catalog(context)
    assert not context.driver.find_elements(By.ID, "product-" + context.delete_id)


@then("the other product should still appear in the catalog")
def check_other_product_kept(context):
    """Check only the chosen product was deleted."""
    wait_for_catalog(context)
    wait_until(
        context,
        EC.visibility_of_element_located((By.ID, "product-" + context.keep_id)),
    )

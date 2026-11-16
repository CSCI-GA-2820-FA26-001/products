"""Steps for deleting products through the UI."""

from uuid import uuid4
import requests
from behave import given, when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def wait_until(context, condition):
    """Wait for a browser condition."""
    return WebDriverWait(context.driver, context.wait_seconds).until(condition)


def create_product(context, role):
    """Create a unique product and show it in the table."""
    response = requests.post(
        f"{context.base_url}/products",
        json={
            "name": f"Delete-{role}-{uuid4().hex[:8]}",
            "description": f"Delete test product ({role})",
            "price": "5.00",
        },
        timeout=10,
    )
    assert response.status_code == 201
    product_id = str(response.json()["id"])
    context.driver.refresh()
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
    context.add_cleanup(
        requests.delete, f"{context.base_url}/products/{context.keep_id}", timeout=10
    )


@when("I delete the product")
def delete_product(context):
    """Click the row's Delete button."""
    wait_until(
        context, EC.element_to_be_clickable((By.ID, "delete-" + context.delete_id))
    ).click()


@then("I should see a product deletion success message")
def check_delete_success(context):
    """Check the success message."""
    wait_until(
        context,
        lambda driver: driver.find_element(By.ID, "flash_message").text
        == "Product deleted successfully.",
    )


@then("the product should no longer appear in the catalog")
def check_product_removed(context):
    """Check the deleted row is gone."""
    wait_until(
        context,
        EC.invisibility_of_element_located((By.ID, "product-" + context.delete_id)),
    )


@then("the other product should still appear in the catalog")
def check_other_product_kept(context):
    """Check only the chosen product was deleted."""
    assert context.driver.find_element(
        By.ID, "product-" + context.keep_id
    ).is_displayed()

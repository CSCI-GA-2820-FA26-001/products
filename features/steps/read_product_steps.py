"""Selenium steps for reading products from their names."""

from decimal import Decimal
from uuid import uuid4

from behave import given, when, then  # pylint: disable=no-name-in-module
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def _wait(context, condition):
    """Wait for an observable browser condition."""
    return WebDriverWait(
        context.driver,
        context.wait_seconds,
    ).until(condition)


def _element(context, element_id):
    """Find a control by its stable ID."""
    return context.driver.find_element(By.ID, element_id)


def _click(context, element_id):
    """Click a visible and enabled control."""
    _wait(
        context,
        EC.element_to_be_clickable((By.ID, element_id)),
    ).click()


def _fill(context, element_id, value):
    """Enter a field value through the browser."""
    element = _element(context, element_id)
    element.clear()

    if value:
        element.send_keys(value)


def _wait_for_catalog(context):
    """Wait for the catalog request to finish successfully."""
    _wait(
        context,
        lambda driver: (
            driver.find_element(
                By.ID,
                "results_status",
            ).get_attribute("data-state")
            == "ready"
            and driver.find_element(
                By.ID,
                "search_results",
            ).get_attribute("aria-busy")
            == "false"
        ),
    )


def _create_product(context, description, price):
    """Create a fixture using the existing Create dialog."""
    name = "Read-" + uuid4().hex[:12]

    _click(context, "open-create-btn")

    _wait(
        context,
        EC.visibility_of_element_located((By.ID, "create-product-dialog")),
    )

    _fill(context, "create_product_name", name)
    _fill(context, "create_product_description", description)
    _fill(context, "create_product_price", price)

    _click(context, "create-btn")

    _wait(
        context,
        EC.visibility_of_element_located((By.ID, "retrieve-product-dialog")),
    )

    _wait(
        context,
        lambda driver: driver.find_element(
            By.ID,
            "flash_message",
        ).text
        == "Product created successfully.",
    )

    product_id = _element(context, "detail_product_id").text.strip()

    assert product_id.isdigit()
    assert int(product_id) > 0
    assert _element(context, "detail_product_name").text == name
    assert (
        _element(
            context,
            "detail_product_description",
        ).text
        == description
    )
    assert Decimal(_element(context, "detail_product_price").text) == Decimal(price)

    _click(context, "close-read-btn")

    _wait(
        context,
        EC.invisibility_of_element_located((By.ID, "retrieve-product-dialog")),
    )

    _click(context, "reset-search-btn")
    _wait_for_catalog(context)

    _wait(
        context,
        EC.element_to_be_clickable((By.ID, "retrieve-" + product_id)),
    )

    return {
        "id": product_id,
        "name": name,
        "description": description,
        "price": Decimal(price),
    }


def _select_product(context, index):
    """Select a fixture using its actual name button."""
    context.read_expected_product = context.read_products[index]

    _click(
        context,
        "retrieve-" + context.read_expected_product["id"],
    )

    _wait(
        context,
        EC.visibility_of_element_located((By.ID, "retrieve-product-dialog")),
    )


@given("a read-test product exists through the UI")
def create_read_product(context):
    """Create one product with a description."""
    context.read_products = [_create_product(context, "A paper notebook", "19.99")]


@given("two read-test products exist through the UI")
def create_two_read_products(context):
    """Create two products with distinct details."""
    context.read_products = [
        _create_product(context, "First product description", "19.99"),
        _create_product(context, "Second product description", "39.50"),
    ]


@given("a read-test product with an empty description exists through the UI")
def create_read_product_without_description(context):
    """Create a product whose description is empty."""
    context.read_products = [_create_product(context, "", "0")]


@when("I select the first read-test product name")
def select_first_product(context):
    """Click the first fixture's product name."""
    _select_product(context, 0)


@when("I select the second read-test product name")
def select_second_product(context):
    """Click the second fixture's product name."""
    _select_product(context, 1)


@then("the details dialog should show the selected product")
def check_read_product(context):
    """Check the saved ID, name, price, and description."""
    _wait(
        context,
        lambda driver: driver.find_element(
            By.ID,
            "retrieve-product-dialog",
        ).get_attribute("data-state")
        in {"ready", "error"},
    )

    dialog = _element(context, "retrieve-product-dialog")

    assert dialog.get_attribute("data-state") == "ready", _element(
        context, "read_message"
    ).text
    assert dialog.get_attribute("aria-busy") == "false"
    assert _element(context, "product_details").is_displayed()

    expected = context.read_expected_product

    assert _element(context, "detail_product_id").text == expected["id"]
    assert _element(context, "detail_product_name").text == expected["name"]
    assert (
        _element(
            context,
            "detail_product_description",
        ).text
        == expected["description"]
    )

    assert Decimal(_element(context, "detail_product_price").text) == expected["price"]


@then("the catalog should have no Description column")
def check_catalog_columns(context):
    """Check the catalog's four-column structure."""
    headings = [
        heading.text
        for heading in context.driver.find_elements(
            By.CSS_SELECTOR,
            "#products_table thead th",
        )
    ]

    assert headings == ["ID", "Product", "Price", "Actions"]


@when("I close the product details dialog")
def close_read_dialog(context):
    """Close details using its visible close button."""
    _click(context, "close-read-btn")

    _wait(
        context,
        EC.invisibility_of_element_located((By.ID, "retrieve-product-dialog")),
    )


@then("the product details dialog should be closed")
def check_read_dialog_closed(context):
    """Check that details are no longer displayed."""
    assert not _element(
        context,
        "retrieve-product-dialog",
    ).is_displayed()

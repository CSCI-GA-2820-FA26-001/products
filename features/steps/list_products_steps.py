"""Selenium steps for the default product catalog."""

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
    """Find an element by its stable ID."""
    return context.driver.find_element(By.ID, element_id)


def _click(context, element_id):
    """Click a visible and enabled control."""
    _wait(
        context,
        EC.element_to_be_clickable((By.ID, element_id)),
    ).click()


def _fill(context, element_id, value):
    """Enter text through the browser."""
    element = _element(context, element_id)
    element.clear()

    if value:
        element.send_keys(value)


def _wait_for_catalog(context):
    """Wait for a successful catalog response."""
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


def _snapshot(context):
    """Read the fields displayed in the four-column catalog."""
    products = {}

    rows = context.driver.find_elements(
        By.CSS_SELECTOR,
        "#products_body tr",
    )

    for row in rows:
        assert len(row.find_elements(By.TAG_NAME, "td")) == 4

        product_id = row.find_element(
            By.CSS_SELECTOR,
            ".product-id-cell",
        ).text.strip()

        assert product_id.isdigit()
        assert int(product_id) > 0
        assert product_id not in products, f"Duplicate product ID: {product_id}"

        name = row.find_element(
            By.CSS_SELECTOR,
            ".product-name-cell",
        ).text

        price = row.find_element(
            By.CSS_SELECTOR,
            ".product-price-cell",
        ).text

        products[product_id] = (name, Decimal(price))

    return products


@given("the following list-test products are created through the UI:")
def create_list_test_products(context):
    """Create fixtures using the existing Create UI."""
    _wait_for_catalog(context)

    context.list_expected_products = _snapshot(context)
    suffix = uuid4().hex[:12]

    for product in context.table:
        name = product["name"] + "-" + suffix
        description = product["description"]
        price = product["price"]

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

        product_id = _element(
            context,
            "detail_product_id",
        ).text.strip()

        assert product_id.isdigit()
        assert int(product_id) > 0
        assert product_id not in context.list_expected_products

        assert _element(context, "detail_product_name").text == name
        assert (
            _element(
                context,
                "detail_product_description",
            ).text
            == description
        )

        assert Decimal(_element(context, "detail_product_price").text) == Decimal(price)

        context.list_expected_products[product_id] = (
            name,
            Decimal(price),
        )

        _click(context, "close-read-btn")

        _wait(
            context,
            EC.invisibility_of_element_located((By.ID, "retrieve-product-dialog")),
        )


@when("I reload the administration page without searching")
def reload_catalog(context):
    """Reload the page to trigger its default list request."""
    context.driver.refresh()
    _wait_for_catalog(context)


@then("the full catalog should include all saved list-test products")
def check_full_catalog(context):
    """Check exact membership and the displayed product fields."""
    _wait_for_catalog(context)

    actual = _snapshot(context)
    expected = context.list_expected_products

    assert actual == expected, f"Expected catalog {expected}, got {actual}"


@then("each displayed product should appear only once")
def check_unique_products(context):
    """Reject duplicate product IDs."""
    _wait_for_catalog(context)
    products = _snapshot(context)

    rows = context.driver.find_elements(
        By.CSS_SELECTOR,
        "#products_body tr",
    )

    assert len(rows) == len(products)


@given("the catalog is empty for the list test")
def require_empty_catalog(context):
    """Require an empty test instance without bypassing the UI."""
    _wait_for_catalog(context)

    assert (
        _snapshot(context) == {}
    ), "Run the empty-catalog scenario against an empty test instance."


@then("the product results table should be empty")
def check_empty_results(context):
    """Check the empty table after a completed request."""
    _wait_for_catalog(context)

    assert (
        context.driver.find_elements(
            By.CSS_SELECTOR,
            "#products_body tr",
        )
        == []
    )


@then("the product list should report no products found")
def check_empty_catalog_message(context):
    """Check the visible empty-catalog message."""
    assert (
        _element(
            context,
            "results_status",
        ).text
        == "No products found."
    )

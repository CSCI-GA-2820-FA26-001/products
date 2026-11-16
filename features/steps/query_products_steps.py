"""Selenium steps for querying products through the UI."""

from decimal import Decimal
from uuid import uuid4

from behave import given, when, then  # pylint: disable=no-name-in-module
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

QUERY_FIELDS = {
    "exact name": "search_name",
    "minimum price": "search_min_price",
    "maximum price": "search_max_price",
}


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


def _wait_for_completion(context):
    """Wait for a completed list or query operation."""
    _wait(
        context,
        lambda driver: (
            driver.find_element(
                By.ID,
                "results_status",
            ).get_attribute("data-state")
            in {
                "ready",
                "invalid",
                "error",
            }
            and driver.find_element(
                By.ID,
                "search_results",
            ).get_attribute("aria-busy")
            == "false"
        ),
    )


def _require_ready(context):
    """Require a successful response with a useful failure message."""
    _wait_for_completion(context)

    status = _element(context, "results_status")
    assert status.get_attribute("data-state") == "ready", status.text


def _snapshot(context):
    """Read IDs, names, and prices from the visible table."""
    products = {}

    for row in context.driver.find_elements(
        By.CSS_SELECTOR,
        "#products_body tr",
    ):
        product_id = row.find_element(
            By.CSS_SELECTOR,
            ".product-id-cell",
        ).text.strip()

        assert product_id not in products, f"Duplicate product ID: {product_id}"

        name = row.find_element(
            By.CSS_SELECTOR,
            ".product-name-cell",
        ).text

        price = Decimal(
            row.find_element(
                By.CSS_SELECTOR,
                ".product-price-cell",
            ).text
        )

        products[product_id] = (name, price)

    return products


def _create_product(context, name, price):
    """Create a fixture using the existing Create UI."""
    _click(context, "open-create-btn")

    _wait(
        context,
        EC.visibility_of_element_located((By.ID, "create-product-dialog")),
    )

    _fill(context, "create_product_name", name)
    _fill(
        context,
        "create_product_description",
        "Query test product",
    )
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
    assert Decimal(_element(context, "detail_product_price").text) == Decimal(price)

    _click(context, "close-read-btn")

    _wait(
        context,
        EC.invisibility_of_element_located((By.ID, "retrieve-product-dialog")),
    )

    return product_id


@given("the following query-test products are created through the UI:")
def create_query_products(context):
    """Prepare fixtures without calling APIs or accessing the database."""
    _require_ready(context)

    context.query_catalog = _snapshot(context)
    context.query_products = {}

    suffix = uuid4().hex[:12]

    for product in context.table:
        name = "Query-" + suffix + "-" + product["name"]
        price = product["price"]

        product_id = _create_product(context, name, price)

        assert product_id not in context.query_catalog

        context.query_catalog[product_id] = (
            name,
            Decimal(price),
        )
        context.query_products[product["alias"]] = {
            "id": product_id,
            "name": name,
        }

    _click(context, "reset-search-btn")
    _require_ready(context)

    assert _snapshot(context) == context.query_catalog


@when('I set the query {field} to "{value}"')
def set_query_field(context, field, value):
    """Enter a filter value through its actual input."""
    assert field in QUERY_FIELDS
    _fill(context, QUERY_FIELDS[field], value)


@when('I use query product "{alias}" as the exact name')
def use_product_name(context, alias):
    """Use a fixture's actual saved name."""
    _fill(
        context,
        "search_name",
        context.query_products[alias]["name"],
    )


@when("I use a missing product name as the exact name")
def use_missing_name(context):
    """Enter a unique name that was not created by the test."""
    _fill(
        context,
        "search_name",
        "Missing-" + uuid4().hex,
    )


@when("I submit the product query")
def submit_query(context):
    """Submit through the Search button and preserve entered values."""
    context.submitted_query_values = {
        field: _element(context, element_id).get_attribute("value")
        for field, element_id in QUERY_FIELDS.items()
    }

    _click(context, "search-btn")


@then("the results should match the query filters")
def check_query_results(context):
    """Check exact membership using the known catalog."""
    _require_ready(context)

    name = (
        _element(
            context,
            "search_name",
        )
        .get_attribute("value")
        .strip()
    )

    minimum = (
        _element(
            context,
            "search_min_price",
        )
        .get_attribute("value")
        .strip()
    )

    maximum = (
        _element(
            context,
            "search_max_price",
        )
        .get_attribute("value")
        .strip()
    )

    minimum = Decimal(minimum) if minimum else None
    maximum = Decimal(maximum) if maximum else None

    expected = {}

    for product_id, details in context.query_catalog.items():
        product_name, price = details

        if name and product_name != name:
            continue

        if minimum is not None and price < minimum:
            continue

        if maximum is not None and price > maximum:
            continue

        expected[product_id] = details

    actual = _snapshot(context)

    assert actual == expected, f"Expected {expected}, got {actual}"

    expected_message = (
        f"{len(expected)} product(s)." if expected else "No products found."
    )

    assert (
        _element(
            context,
            "results_status",
        ).text
        == expected_message
    )


@then("the query should show no matching products")
def check_no_query_results(context):
    """Check that a successful empty query replaces previous rows."""
    _require_ready(context)

    assert _snapshot(context) == {}
    assert (
        _element(
            context,
            "results_status",
        ).text
        == "No products found."
    )


@then('the query should report "{message}" for {field}')
def check_query_validation(context, message, field):
    """Check validation, empty results, and preserved inputs."""
    _wait_for_completion(context)

    status = _element(context, "results_status")

    assert status.get_attribute("data-state") == "invalid"
    assert status.text == "Please correct the search filters."
    assert _snapshot(context) == {}

    element_id = QUERY_FIELDS[field]

    assert (
        _element(
            context,
            element_id,
        ).get_attribute("aria-invalid")
        == "true"
    )

    assert (
        _element(
            context,
            element_id + "_error",
        ).text
        == message
    )

    for field_name, expected_value in context.submitted_query_values.items():
        assert (
            _element(
                context,
                QUERY_FIELDS[field_name],
            ).get_attribute("value")
            == expected_value
        )

"""Selenium steps for the shared Products administration UI."""

from behave import given, when, then  # pylint: disable=no-name-in-module
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

CREATE_FIELDS = [
    "create_product_name",
    "create_product_description",
    "create_product_price",
]

SEARCH_FIELDS = [
    "search_name",
    "search_min_price",
    "search_max_price",
]


def _element(context, element_id):
    """Find an element by its stable ID."""
    return context.driver.find_element(By.ID, element_id)


def _wait(context, condition):
    """Wait for a browser condition."""
    return WebDriverWait(
        context.driver,
        context.wait_seconds,
    ).until(condition)


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
    element.send_keys(value)


def _wait_for_products(context):
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


def _result_rows(context):
    """Read result rows without depending on their ordering."""
    return sorted(
        row.text
        for row in context.driver.find_elements(
            By.CSS_SELECTOR,
            "#products_body tr",
        )
    )


@given("I am on the Products administration page")
@when("I open the Products administration page")
def open_admin_page(context):
    """Open the page and wait for the initial catalog."""
    context.driver.get(context.base_url)

    _wait(
        context,
        EC.visibility_of_element_located((By.ID, "page-title")),
    )
    _wait_for_products(context)

    context.original_rows = _result_rows(context)


@then("I should see the Products administration page")
def check_admin_page(context):
    """Check the page title and heading."""
    assert context.driver.title == "Products Administration"

    heading = _element(context, "page-title")
    assert heading.is_displayed()
    assert heading.text == "Products Administration"


@then("I should see the shared product management controls")
def check_shared_controls(context):
    """Check the visible page controls."""
    for element_id in [
        "open-create-btn",
        *SEARCH_FIELDS,
        "search-btn",
        "reset-search-btn",
        "search_results",
        "products_table",
    ]:
        assert _element(context, element_id).is_displayed()

    assert not context.driver.find_elements(By.ID, "list-all-btn")
    assert not context.driver.find_elements(By.ID, "product_form")
    assert not context.driver.find_elements(By.ID, "feedback_form")


@then("the default product list should be loaded")
def check_default_list(context):
    """Check successful loading, including an empty catalog."""
    _wait_for_products(context)

    rows = _result_rows(context)
    expected = f"{len(rows)} product(s)." if rows else "No products found."

    assert _element(context, "results_status").text == expected


@when("I open the create product dialog")
def open_create_dialog(context):
    """Open the existing Create dialog."""
    _click(context, "open-create-btn")

    _wait(
        context,
        EC.visibility_of_element_located((By.ID, "create-product-dialog")),
    )


@then("I should see the create product fields")
def check_create_fields(context):
    """Check the visible creation fields."""
    for element_id in CREATE_FIELDS:
        assert _element(context, element_id).is_displayed()


@when("I cancel the create product dialog")
def cancel_create_dialog(context):
    """Close the unsaved dialog."""
    _click(context, "cancel-create-btn")


@then("the create product dialog should be closed")
def check_dialog_closed(context):
    """Check that the dialog is hidden."""
    assert not _element(
        context,
        "create-product-dialog",
    ).is_displayed()


@when("I enter product details without saving")
def enter_unsaved_details(context):
    """Enter an unsaved draft."""
    for element_id, value in zip(
        CREATE_FIELDS,
        ["Notebook", "Draft details", "19.99"],
    ):
        _fill(context, element_id, value)


@given("an operation message is displayed")
@when("an operation message is displayed")
def display_operation_message(context):
    """Produce a validation message through actual UI controls."""
    _fill(context, "create_product_price", "-1")
    _click(context, "create-btn")

    _wait(
        context,
        lambda driver: driver.find_element(
            By.ID,
            "create_message",
        ).text
        == "Price must be a finite, non-negative number.",
    )


@when("I clear the product form")
def clear_product_form(context):
    """Clear the draft using its button."""
    _click(context, "clear-btn")


@then("the product fields and operation messages should be empty")
def check_cleared_form(context):
    """Check cleared inputs and messages."""
    for element_id in CREATE_FIELDS:
        assert _element(context, element_id).get_attribute("value") == ""

    for element_id in ["flash_message", "create_message"]:
        assert _element(context, element_id).text == ""


@then("the create product dialog should remain open")
def check_dialog_open(context):
    """Clearing a draft keeps its dialog open."""
    assert _element(
        context,
        "create-product-dialog",
    ).is_displayed()


@then("the product results should be unchanged")
def check_results_unchanged(context):
    """Check that the catalog still contains the original rows."""
    _wait_for_products(context)
    assert _result_rows(context) == context.original_rows


@then("unfinished product actions should be disabled")
def check_disabled_actions(context):
    """Query and Feedback remain separate stories."""
    for element_id in [
        "search-btn",
        "submit-feedback-btn",
    ]:
        assert not _element(context, element_id).is_enabled()

    assert _element(context, "open-create-btn").is_enabled()
    assert _element(context, "reset-search-btn").is_enabled()


@then("the create button should be enabled")
def check_create_enabled(context):
    """The existing Create feature remains available."""
    button = _element(context, "create-btn")
    assert button.is_displayed()
    assert button.is_enabled()


@then("the draft controls should be enabled")
def check_draft_controls(context):
    """Clear and close controls remain usable."""
    for element_id in [
        "clear-btn",
        "cancel-create-btn",
        "close-create-btn",
    ]:
        element = _element(context, element_id)
        assert element.is_displayed()
        assert element.is_enabled()


@when("I enter search filters")
def enter_search_filters(context):
    """Populate inputs without submitting a search."""
    for element_id, value in zip(
        SEARCH_FIELDS,
        ["Notebook", "10", "30"],
    ):
        _fill(context, element_id, value)


@when("I reset the search filters")
def reset_search(context):
    """Clear filters and wait for the complete catalog."""
    _click(context, "reset-search-btn")
    _wait_for_products(context)


@then("the search inputs should be empty")
def check_empty_filters(context):
    """Check all filter values."""
    for element_id in SEARCH_FIELDS:
        assert _element(context, element_id).get_attribute("value") == ""

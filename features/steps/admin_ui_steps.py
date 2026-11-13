"""Selenium steps for the shared UI without business API integration."""

from behave import given, when, then  # pylint: disable=no-name-in-module
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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


def _click(context, element_id):
    """Wait for an enabled, visible control before clicking."""
    WebDriverWait(
        context.driver,
        context.wait_seconds,
    ).until(EC.element_to_be_clickable((By.ID, element_id))).click()


def _fill(context, element_id, value):
    """Enter text through the browser."""
    element = _element(context, element_id)
    element.clear()
    element.send_keys(value)


def _result_rows(context):
    """Read the current result rows through Selenium."""
    return [
        row.text
        for row in context.driver.find_elements(
            By.CSS_SELECTOR,
            "#products_body tr",
        )
    ]


@given("I am on the Products administration page")
@when("I open the Products administration page")
def open_admin_page(context):
    """Open the shared UI and wait for its initialization."""
    context.driver.get(context.base_url)

    WebDriverWait(
        context.driver,
        context.wait_seconds,
    ).until(
        lambda driver: driver.execute_script(
            "return typeof window.ProductsUI === 'object';"
        )
    )

    context.original_rows = _result_rows(context)


@then("I should see the Products administration page")
def check_admin_page(context):
    """Check the title and visible heading."""
    assert context.driver.title == "Products Administration"

    heading = _element(context, "page-title")

    assert heading.is_displayed()
    assert heading.text == "Products Administration"


@then("I should see the shared product management controls")
def check_shared_controls(context):
    """Check controls belonging to the main page."""
    for element_id in [
        "open-create-btn",
        *SEARCH_FIELDS,
        "search-btn",
        "reset-search-btn",
        "search_results",
        "products_table",
    ]:
        assert _element(context, element_id).is_displayed()

    assert not context.driver.find_elements(
        By.ID,
        "list-all-btn",
    )

    assert not context.driver.find_elements(
        By.ID,
        "product_form",
    )

    assert not context.driver.find_elements(
        By.ID,
        "feedback_form",
    )


@then("product listing should be marked as unavailable")
def check_listing_unavailable(context):
    """Do not present an unloaded catalog as an empty saved catalog."""
    status = _element(context, "results_status")

    assert status.get_attribute("data-state") == "unavailable"
    assert status.text == "Product listing is not available yet."


@when("I open the create product dialog")
def open_create_dialog(context):
    """Open the draft dialog using its entry button."""
    _click(context, "open-create-btn")

    WebDriverWait(
        context.driver,
        context.wait_seconds,
    ).until(EC.visibility_of_element_located((By.ID, "create-product-dialog")))


@then("I should see the create product fields")
def check_create_fields(context):
    """Check visible creation fields."""
    for element_id in CREATE_FIELDS:
        assert _element(context, element_id).is_displayed()


@when("I cancel the create product dialog")
def cancel_create_dialog(context):
    """Close the dialog without a business operation."""
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
    """Enter a draft using Selenium inputs."""
    for element_id, value in zip(
        CREATE_FIELDS,
        ["Notebook", "Draft details", "19.99"],
    ):
        _fill(context, element_id, value)


@given("an operation message is displayed")
@when("an operation message is displayed")
def display_operation_message(context):
    """Exercise the shared UI message helper without an API or database."""
    context.driver.execute_script(
        "window.ProductsUI.showMessage('Unsaved draft', 'info');"
    )

    assert (
        _element(
            context,
            "create_message",
        ).text
        == "Unsaved draft"
    )


@when("I clear the product form")
def clear_product_form(context):
    """Use the actual Clear control inside the create dialog."""
    _click(context, "clear-btn")


@then("the product fields and operation messages should be empty")
def check_cleared_form(context):
    """Check both the draft fields and shared message regions."""
    for element_id in CREATE_FIELDS:
        assert (
            _element(
                context,
                element_id,
            ).get_attribute("value")
            == ""
        )

    for element_id in [
        "flash_message",
        "create_message",
    ]:
        assert _element(context, element_id).text == ""


@then("the create product dialog should remain open")
def check_dialog_open(context):
    """Clear keeps the dialog available for further editing."""
    assert _element(
        context,
        "create-product-dialog",
    ).is_displayed()


@then("the product results should be unchanged")
def check_results_unchanged(context):
    """Check that clearing a draft did not change the displayed results."""
    assert _result_rows(context) == context.original_rows


@then("unfinished product actions should be disabled")
def check_disabled_actions(context):
    """Check static business controls, including those in closed dialogs."""
    for element_id in [
        "search-btn",
        "create-btn",
        "update-btn",
        "submit-feedback-btn",
    ]:
        assert not _element(context, element_id).is_enabled()

    assert _element(context, "open-create-btn").is_enabled()


@then("the create button should be disabled")
def check_create_disabled(context):
    """The dialog can open while saving remains unavailable."""
    button = _element(context, "create-btn")

    assert button.is_displayed()
    assert not button.is_enabled()


@then("the draft controls should be enabled")
def check_draft_controls(context):
    """Clear and Cancel remain usable."""
    for element_id in [
        "clear-btn",
        "cancel-create-btn",
        "close-create-btn",
    ]:
        assert _element(context, element_id).is_displayed()
        assert _element(context, element_id).is_enabled()


@when("I enter search filters")
def enter_search_filters(context):
    """Populate filters without performing a search."""
    for element_id, value in zip(
        SEARCH_FIELDS,
        ["Notebook", "10", "30"],
    ):
        _fill(context, element_id, value)


@when("I reset the search filters")
def reset_search(context):
    """Reset only the local input fields."""
    _click(context, "reset-search-btn")


@then("the search inputs should be empty")
def check_empty_filters(context):
    """Check that Reset filters clears all search inputs."""
    for element_id in SEARCH_FIELDS:
        assert (
            _element(
                context,
                element_id,
            ).get_attribute("value")
            == ""
        )

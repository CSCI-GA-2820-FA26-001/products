"""Steps for reviewing products through the UI."""

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


def resolve(value):
    """Translate table keywords into real input."""
    return {"empty": "", "spaces": "   ", "valid": "Review-" + uuid4().hex[:8]}.get(
        value, value
    )


def displayed_reviews(driver):
    """Read (rating, text) pairs from the saved reviews table."""
    rows = driver.find_elements(By.CSS_SELECTOR, "#feedback_body tr")
    return [
        tuple(cell.text for cell in row.find_elements(By.TAG_NAME, "td"))
        for row in rows
    ]


def submit_review(context, rating, text):
    """Fill in the review form and submit it."""
    for element_id, value in (
        ("product_rating", rating),
        ("product_review_text", text),
    ):
        element = wait_until(
            context, EC.visibility_of_element_located((By.ID, element_id))
        )
        element.clear()
        if value:
            element.send_keys(value)
    click(context, "submit-feedback-btn")


def submit_valid_review(context, rating):
    """Submit a uniquely worded review, remember it and wait for the result."""
    text = "Review-" + uuid4().hex[:8]
    submit_review(context, rating, text)
    context.reviews.append((rating, text))
    wait_until(
        context, lambda driver: driver.find_element(By.ID, "review_message").text != ""
    )


@given("a product has been created through the UI")
def create_product_to_review(context):
    """Create a unique product with the Create dialog and show it in the table."""
    click(context, "open-create-btn")
    for field, value in [
        ("name", "Review-" + uuid4().hex[:8]),
        ("description", "Review test product"),
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
    context.review_id = context.driver.find_element(
        By.ID, "detail_product_id"
    ).text.strip()
    context.driver.find_element(
        By.CSS_SELECTOR, "#retrieve-product-dialog [data-close]"
    ).click()
    click(context, "reset-search-btn")
    wait_until(
        context,
        EC.visibility_of_element_located((By.ID, "product-" + context.review_id)),
    )
    context.reviews = []


@when("I open the product's reviews")
def open_reviews(context):
    """Click the row's Review button."""
    click(context, "review-" + context.review_id)
    wait_until(
        context, EC.visibility_of_element_located((By.ID, "review-product-dialog"))
    )


@when("I submit a valid review")
def submit_first_review(context):
    """Submit a valid review."""
    submit_valid_review(context, "5")


@when("I submit another valid review")
def submit_second_review(context):
    """Submit a second valid review with a different rating."""
    submit_valid_review(context, "3")


@when('I submit a valid review with rating "{rating}"')
def submit_review_with_rating(context, rating):
    """Submit a valid review with a specific rating."""
    submit_valid_review(context, rating)


@when('I submit a review with rating "{rating}" and text "{text}"')
def submit_invalid_review(context, rating, text):
    """Submit a review that should be rejected."""
    submit_review(context, resolve(rating), resolve(text))


@when("the product is deleted in another window")
def delete_in_another_window(context):
    """Delete the product in a second tab while the review dialog stays open."""
    original = context.driver.current_window_handle
    context.driver.switch_to.new_window("tab")
    context.driver.get(context.base_url)
    click(context, "delete-" + context.review_id)
    wait_until(
        context,
        EC.invisibility_of_element_located((By.ID, "product-" + context.review_id)),
    )
    context.driver.close()
    context.driver.switch_to.window(original)


@then("I should see a review success message")
def check_review_success(context):
    """Check the success message."""
    wait_until(
        context,
        lambda driver: driver.find_element(By.ID, "review_message").text
        == "Review submitted successfully.",
    )


@then('I should see the review error "{message}"')
def check_review_error(context, message):
    """Check the error message."""
    wait_until(
        context,
        lambda driver: driver.find_element(By.ID, "review_message").text == message,
    )


@then("the saved review should be displayed")
def check_saved_review(context):
    """Check the latest review is in the saved reviews table."""
    wait_until(context, lambda driver: context.reviews[-1] in displayed_reviews(driver))


@then("both reviews should be displayed")
def check_both_reviews(context):
    """Check earlier reviews were preserved."""
    wait_until(
        context,
        lambda driver: all(
            review in displayed_reviews(driver) for review in context.reviews
        ),
    )


@then("no reviews should be saved")
def check_no_reviews(context):
    """Reload the page and check the product still has no reviews."""
    context.driver.refresh()
    open_reviews(context)
    wait_until(
        context,
        lambda driver: driver.find_element(By.ID, "reviews_status").text
        == "No reviews yet.",
    )
    assert displayed_reviews(context.driver) == []

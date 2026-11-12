"""
Web steps: interact with the service through the browser (Selenium) only
"""

from behave import when, then  # pylint: disable=no-name-in-module


@when('I visit the "Home Page"')
def step_impl(context):
    """Open the service's root URL in the browser"""
    context.driver.get(context.base_url)


@then("the browser should be at the configured service URL")
def step_impl(context):  # pylint: disable=function-redefined
    """The browser opened BASE_URL"""
    assert context.driver.current_url.startswith(
        context.base_url
    ), f"Expected {context.base_url}, got {context.driver.current_url}"


@then('I should see "{text}" in the page')
def step_impl(context, text):  # pylint: disable=function-redefined
    """The page body contains the text"""
    assert text in context.driver.page_source


@then('I should not see "{text}" in the page')
def step_impl(context, text):  # pylint: disable=function-redefined
    """The page body does not contain the text"""
    assert text not in context.driver.page_source

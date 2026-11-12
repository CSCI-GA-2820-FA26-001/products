Feature: BDD environment smoke test
    As a developer
    I need a working Selenium and Behave testing environment
    So that the team can test the Products UI through a browser

Scenario: Run a browser test
    When I visit the "Home Page"
    Then the browser should be at the configured service URL
    And I should see "Product" in the page
    And I should not see "404 Not Found" in the page
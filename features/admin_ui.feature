Feature: Shared Products administration page
  As a store administrator
  I need a shared administration page
  So that product management features can be connected in one place

  Background:
    Given I am on the Products administration page

  Scenario: Open the administration page
    Then I should see the Products administration page
    And I should see the shared product management controls
    And product listing should be marked as unavailable

  Scenario: Open and close the create product dialog
    When I open the create product dialog
    Then I should see the create product fields
    When I cancel the create product dialog
    Then the create product dialog should be closed

  Scenario: Clear an unsaved product draft
    When I open the create product dialog
    And I enter product details without saving
    And an operation message is displayed
    And I clear the product form
    Then the product fields and operation messages should be empty
    And the create product dialog should remain open
    And the product results should be unchanged

  Scenario: Identify unavailable business features
    Then unfinished product actions should be disabled
    When I open the create product dialog
    Then the create button should be disabled
    And the draft controls should be enabled

  Scenario: Reset search inputs
    When I enter search filters
    And I reset the search filters
    Then the search inputs should be empty
    And product listing should be marked as unavailable
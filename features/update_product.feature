@update_product
Feature: Update products through the administration page
  As a store administrator
  I want to edit a product in its Update dialog
  So that the catalog stays accurate

  Background:
    Given an Update test product has been created through the UI
    And I open that product's Update dialog

  Scenario: Save changes and preserve the product ID
    When I enter updated product details
    And I save the Update dialog
    Then the Update dialog reports success
    When I reopen that product's Update dialog
    Then the updated product details and original ID are displayed

  Scenario: Reject a negative price without saving changes
    When I enter a negative price in the Update dialog
    And I save the Update dialog
    Then the Update dialog reports an invalid price
    When I reopen that product's Update dialog
    Then the original product details and ID are displayed

  @requires_feedback_ui
  Scenario: Preserve existing feedback
    Given I submit a review for the Update test product through the UI
    And I open that product's Update dialog
    When I enter updated product details
    And I save the Update dialog
    Then the Update dialog reports success
    When I reopen that product's Update dialog
    Then the updated product details and original ID are displayed
    And its original review is still displayed through the UI

  @requires_delete_ui
  Scenario: Product deleted while the Update dialog is open
    Given I delete the Update test product through another browser tab
    When I enter updated product details
    And I save the Update dialog
    Then the Update dialog reports that the product was not found
    And refreshing the page shows that the original product is absent

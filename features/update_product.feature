@update_product
Feature: Update products through the administration page
  As a store administrator
  I want to update a product through the administration page
  So that I can keep product information accurate

  Background:
    Given I am on the product administration page
    And I have created the following product through the UI:
      | name            | description       | price |
      | Update BDD Item | Original details  | 19.99 |
    And I have retrieved that product through the UI

  Scenario: Update a product and preserve its ID
    When I change the product details to:
      | name                    | description     | price |
      | Updated BDD Item        | Updated details | 24.50 |
    And I save the product changes
    Then I should see a product update success message
    And the displayed product ID should match the original ID
    When I clear the product form
    And I retrieve the product again using its original ID
    Then the product form should contain:
      | name                    | description     | price |
      | Updated BDD Item        | Updated details | 24.50 |
    And the displayed product ID should match the original ID

  Scenario: Reject a negative price without changing the saved product
    When I change the product price to "-1.00"
    And I save the product changes
    Then I should see a price validation message
    When I clear the product form
    And I retrieve the product again using its original ID
    Then the product form should contain:
      | name            | description      | price |
      | Update BDD Item | Original details | 19.99 |
    And the displayed product ID should match the original ID

  Scenario: Preserve existing feedback when updating product details
    Given I have submitted the following feedback for that product through the UI:
      | rating | text         |
      | 5      | Good quality |
    And I have retrieved that product through the UI
    When I change the product details to:
      | name             | description     | price |
      | Updated BDD Item | Updated details | 24.50 |
    And I save the product changes
    Then I should see a product update success message
    When I clear the product form
    And I retrieve the product again using its original ID
    Then the product form should contain:
      | name             | description     | price |
      | Updated BDD Item | Updated details | 24.50 |
    And the displayed product ID should match the original ID
    And the product feedback should still contain exactly the original review:
      | rating | text         |
      | 5      | Good quality |

  Scenario: Update a product that was deleted after it was retrieved
    Given I have deleted that product through the UI in another browser tab
    And I have returned to the original tab with the loaded product form
    When I change the product details to:
      | name             | description     | price |
      | Updated BDD Item | Updated details | 24.50 |
    And I save the product changes
    Then I should see a product not found message
    And I should not see a product update success message
    When I retrieve the product again using its original ID
    Then I should see a product not found message
    When I list all products through the UI
    Then no product named "Updated BDD Item" should appear

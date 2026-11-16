@delete_product
Feature: Delete products through the administration page
  As a store administrator
  I need to delete products through the UI
  So that I can remove them from the catalog

  Background:
    Given I am on the Products administration page
    And a product exists in the catalog

  Scenario: Delete a product
    When I delete the product
    Then I should see a product deletion success message
    And the product should no longer appear in the catalog

  Scenario: Keep other products when deleting one
    Given another product exists in the catalog
    When I delete the product
    Then the product should no longer appear in the catalog
    And the other product should still appear in the catalog

  Scenario: Keep a deleted product removed after reloading
    When I delete the product
    And I reload the administration page without searching
    Then the product should no longer appear in the catalog
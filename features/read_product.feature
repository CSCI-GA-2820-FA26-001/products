@read_product
Feature: Read a product by selecting its name
  As a store administrator
  I need to open a product from the catalog
  So that I can inspect its saved details

  Background:
    Given I am on the Products administration page

  Scenario: Open product details from its name
    Given a read-test product exists through the UI
    When I select the first read-test product name
    Then the details dialog should show the selected product
    And the catalog should have no Description column
    When I close the product details dialog
    Then the product details dialog should be closed

  Scenario: Read a different product
    Given two read-test products exist through the UI
    When I select the first read-test product name
    Then the details dialog should show the selected product
    When I close the product details dialog
    And I select the second read-test product name
    Then the details dialog should show the selected product

  Scenario: Read a product with an empty description
    Given a read-test product with an empty description exists through the UI
    When I select the first read-test product name
    Then the details dialog should show the selected product
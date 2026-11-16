@list_products
Feature: Display all products without searching
  As a store administrator
  I need the full catalog to appear without searching
  So that I can inspect all saved products

  Background:
    Given I am on the Products administration page

  Scenario: Load products automatically
    Then the search inputs should be empty
    And the default product list should be loaded
    And each displayed product should appear only once

  Scenario: Display products created through the UI
    Given the following list-test products are created through the UI:
      | name     | description      | price |
      | Notebook | A paper notebook | 19.99 |
      | Pencil   | A wooden pencil  | 1.50  |
    When I reload the administration page without searching
    Then the full catalog should include all saved list-test products

  Scenario: Refresh the catalog without duplicate rows
    Given the following list-test products are created through the UI:
      | name     | description      | price |
      | Notebook | A paper notebook | 19.99 |
      | Pencil   | A wooden pencil  | 1.50  |
    When I reload the administration page without searching
    And I reload the administration page without searching
    Then the full catalog should include all saved list-test products
    And each displayed product should appear only once

  Scenario: Reset filters to display the full catalog
    Given the following list-test products are created through the UI:
      | name     | description      | price |
      | Notebook | A paper notebook | 19.99 |
      | Pencil   | A wooden pencil  | 1.50  |
    When I enter search filters
    And I reset the search filters
    Then the search inputs should be empty
    And the full catalog should include all saved list-test products

  @empty_catalog
  Scenario: Display an empty catalog
    Given the catalog is empty for the list test
    When I reload the administration page without searching
    Then the product results table should be empty
    And the product list should report no products found
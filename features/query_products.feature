@query_products
Feature: Query products through the administration page
  As a store administrator
  I need to filter products by exact name and price
  So that I can find products matching my criteria

  Background:
    Given I am on the Products administration page
    And the following query-test products are created through the UI:
      | alias | name           | price |
      | low   | Notebook       | 5.00  |
      | mid   | Notebook       | 10.00 |
      | high  | Notebook       | 20.00 |
      | stand | Notebook Stand | 10.00 |
      | free  | Sticker        | 0     |

  Scenario: Search by exact name
    When I use query product "low" as the exact name
    And I submit the product query
    Then the results should match the query filters

  Scenario: Search by minimum price
    When I set the query minimum price to "10"
    And I submit the product query
    Then the results should match the query filters

  Scenario: Search by maximum price
    When I set the query maximum price to "10"
    And I submit the product query
    Then the results should match the query filters

  Scenario: Include both price boundaries
    When I set the query minimum price to "5"
    And I set the query maximum price to "10"
    And I submit the product query
    Then the results should match the query filters

  Scenario: Combine exact name and price filters
    When I use query product "low" as the exact name
    And I set the query minimum price to "5"
    And I set the query maximum price to "10"
    And I submit the product query
    Then the results should match the query filters

  Scenario: Allow equal minimum and maximum prices
    When I set the query minimum price to "10"
    And I set the query maximum price to "10"
    And I submit the product query
    Then the results should match the query filters

  Scenario: Accept zero as a price filter
    When I set the query minimum price to "0"
    And I set the query maximum price to "0"
    And I submit the product query
    Then the results should match the query filters

  Scenario: Search with blank filters
    When I submit the product query
    Then the results should match the query filters

  Scenario: Find no matching products
    When I use a missing product name as the exact name
    And I submit the product query
    Then the query should show no matching products

  Scenario: Reset a filtered list
    When I use query product "low" as the exact name
    And I submit the product query
    Then the results should match the query filters
    When I reset the search filters
    Then the search inputs should be empty
    And the results should match the query filters

  Scenario: Reject a reversed price range
    When I set the query minimum price to "20"
    And I set the query maximum price to "5"
    And I submit the product query
    Then the query should report "Maximum price must be greater than or equal to minimum price." for maximum price

  Scenario Outline: Reject invalid prices
    When I set the query <field> to "<value>"
    And I submit the product query
    Then the query should report "<message>" for <field>

    Examples:
      | field         | value    | message                                                   |
      | minimum price | -1       | Minimum price must be a finite, non-negative number.       |
      | maximum price | -0.01    | Maximum price must be a finite, non-negative number.       |
      | minimum price | abc      | Minimum price must be a finite, non-negative number.       |
      | maximum price | NaN      | Maximum price must be a finite, non-negative number.       |
      | minimum price | Infinity | Minimum price must be a finite, non-negative number.       |
      | maximum price | 1e309    | Maximum price must be a finite, non-negative number.       |

  Scenario: Correct an invalid filter
    When I set the query minimum price to "abc"
    And I submit the product query
    Then the query should report "Minimum price must be a finite, non-negative number." for minimum price
    When I set the query minimum price to "5"
    And I submit the product query
    Then the results should match the query filters
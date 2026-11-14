@create_product
Feature: Create products through the administration page
  As a store administrator
  I need to create products through the UI
  So that I can add them to the catalog

  Background:
    Given I am on the Products administration page
    When I open the create product dialog

  Scenario Outline: Create a product
    When I fill in a new product with price "<price>"
    And I submit the new product
    Then I should see the saved product details and generated ID
    And I should see a product creation success message

    Examples:
      | price |
      | 19.99 |
      | 0     |

  Scenario Outline: Reject invalid input
    When I fill in a new product with price "19.99"
    And I set the new product's <field> to "<value>"
    And I submit the new product
    Then I should see the creation error "<message>"
    And the Create dialog should keep the entered values

    Examples:
      | field | value | message                                        |
      | name  | empty | Name must contain 1 to 63 characters.           |
      | name  | spaces | Name must contain 1 to 63 characters.          |
      | price | -1    | Price must be a finite, non-negative number.    |
      | price | empty | Price must be a finite, non-negative number.    |

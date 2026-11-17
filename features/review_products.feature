@review_product
Feature: Review products through the administration page
  As a store administrator
  I need to submit and view product feedback through the administration page
  So that I can record and inspect feedback for a product

  Background:
    Given I am on the Products administration page
    And a product has been created through the UI
    When I open the product's reviews

  Scenario: Submit product feedback
    When I submit a valid review
    Then I should see a review success message
    And the saved review should be displayed
    When I reload the administration page without searching
    And I open the product's reviews
    Then the saved review should be displayed

  Scenario: Preserve earlier reviews
    When I submit a valid review
    And I submit another valid review
    Then both reviews should be displayed

  Scenario Outline: Accept boundary ratings
    When I submit a valid review with rating "<rating>"
    Then I should see a review success message
    And the saved review should be displayed

    Examples:
      | rating |
      | 1      |
      | 5      |

  Scenario Outline: Reject invalid feedback
    When I submit a review with rating "<rating>" and text "<text>"
    Then I should see the review error "<message>"
    And no reviews should be saved

    Examples:
      | rating | text   | message                                    |
      | 0      | valid  | Rating must be a whole number from 1 to 5. |
      | 6      | valid  | Rating must be a whole number from 1 to 5. |
      | 3.5    | valid  | Rating must be a whole number from 1 to 5. |
      | empty  | valid  | Rating must be a whole number from 1 to 5. |
      | 3      | empty  | Review text must not be blank.             |
      | 3      | spaces | Review text must not be blank.             |

  Scenario: Submit feedback for an unknown product
    When the product is deleted in another window
    And I submit a valid review
    Then I should see the review error "Product was not found."
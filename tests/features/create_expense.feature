# language: en
Feature: Add and categorize an expense
  As a user
  I want to register an expense with a useful category
  So that my spending history is complete and consistent

  Background:
    Given today is "2026-09-09"
    And the expense store is empty
    And the user is on the new expense page

  Scenario: Save a valid expense with the suggested category
    When the user enters the following expense:
      | description | amount | date       |
      | Netto       | 125.50 | 2026-09-08 |
    Then the suggested category is "Mad"
    When the user saves the expense
    Then exactly 1 expense is stored
    And the expense list contains:
      | description | amount | date       | category | status |
      | Netto       | 125.50 | 2026-09-08 | Mad      | actual |

  Scenario Outline: Do not save when a required field is missing
    When the user enters description "<description>", amount "<amount>" and date "<date>"
    And the user saves the expense
    Then a validation message is shown for "<missing field>"
    And no expense is stored

    Examples:
      | description | amount | date       | missing field |
      |             | 125.50 | 2026-09-08 | description   |
      | Netto       |        | 2026-09-08 | amount        |
      | Netto       | 125.50 |            | date          |

  Scenario Outline: Suggest a category from a known description
    When the user enters description "<description>"
    Then the suggested category is "<category>"

    Examples:
      | description | category                     |
      | Netto       | Mad                          |
      | Matas       | Kosmetik og personlig pleje |
      | DSB         | Transport                    |
      | Netflix     | Underholdning                |

  Scenario: Preserve the category explicitly selected by the user
    When the user enters the following expense:
      | description | amount | date       |
      | Netto       | 125.50 | 2026-09-08 |
    Then the suggested category is "Mad"
    When the user selects category "Shopping"
    And the user saves the expense
    Then the stored expense has category "Shopping"

  Scenario: Only supported categories can be selected
    When the user opens the category selector
    Then the available categories are exactly:
      | category                     |
      | Mad                          |
      | Transport                    |
      | Bolig                        |
      | Underholdning                |
      | Kosmetik og personlig pleje |
      | Shopping                     |
      | Abonnementer                 |
      | Andet                        |

# language: en
Feature: Planned future expenses
  As a user
  I want to register and resolve expected future payments
  So that only payments that actually happen count as expenses

  Background:
    Given today is "2026-09-09"

  Scenario: Save an expense dated in the future as planned
    Given the expense store is empty
    And the user is on the new expense page
    When the user enters the following expense:
      | description | amount | date       |
      | Insurance   | 800.00 | 2026-10-01 |
    And the user saves the expense
    Then the expense is stored with status "planned"
    And it is not included in actual expense totals

  Scenario: Do not ask for confirmation before the planned date
    Given this planned expense exists:
      | id | description | amount | date       | category |
      | 51 | Insurance   | 800.00 | 2026-09-10 | Andet    |
    When the user opens the application
    Then no confirmation is requested for expense "51"

  Scenario Outline: Ask for confirmation when a planned expense is due
    Given today is "<today>"
    And this planned expense exists:
      | id | description | amount | date       | category |
      | 51 | Insurance   | 800.00 | 2026-09-09 | Andet    |
    When the user opens the <location>
    Then the user is asked whether expense "51" took place

    Examples:
      | today      | location                  |
      | 2026-09-09 | application               |
      | 2026-09-10 | relevant monthly overview |

  Scenario: Confirm that a due planned expense took place
    Given this due planned expense exists:
      | id | description | amount | date       | category |
      | 51 | Insurance   | 800.00 | 2026-09-09 | Andet    |
    When the user confirms that expense "51" took place
    Then expense "51" has status "actual"
    And 800.00 DKK is included in the actual total for "2026-09"

  Scenario: Reject a due planned expense
    Given this due planned expense exists:
      | id | description | amount | date       | category |
      | 51 | Insurance   | 800.00 | 2026-09-09 | Andet    |
    When the user states that expense "51" did not take place
    Then expense "51" is not an actual expense
    And 800.00 DKK is not included in the actual total for "2026-09"

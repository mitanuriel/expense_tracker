# language: en
Feature: Delete an expense
  As a user
  I want to remove an incorrectly registered expense
  So that it is no longer part of my records

  Background:
    Given the following actual expense exists:
      | id | description | amount | date       | category |
      | 42 | Netto       | 99.95  | 2026-09-08 | Mad      |

  Scenario: Confirm deletion
    When the user chooses to delete expense "42"
    Then a deletion confirmation is shown
    When the user confirms the deletion
    Then expense "42" no longer exists
    And expense "42" is not shown in the expense list

  Scenario: Cancel deletion
    When the user chooses to delete expense "42"
    And the user cancels the deletion
    Then expense "42" still exists unchanged
    And expense "42" is shown in the expense list

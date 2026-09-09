# language: en
Feature: Monthly expense overview
  As a user
  I want expenses summarized by category and month
  So that I can understand where my money goes

  Background:
    Given today is "2026-09-09"
    And the following actual expenses exist:
      | description | amount  | date       | category      |
      | Groceries   | 2500.00 | 2026-08-02 | Mad           |
      | Train       | 700.00  | 2026-08-11 | Transport     |
      | Cinema      | 450.00  | 2026-08-18 | Underholdning |
      | Clothes     | 1000.00 | 2026-08-23 | Shopping      |
      | Groceries   | 300.00  | 2026-09-01 | Mad           |

  Scenario: Group the selected month's expenses by category
    Given the selected month is "2026-08"
    When the user opens the monthly overview
    Then a chart is displayed
    And the chart contains these category totals:
      | category      | amount  |
      | Mad           | 2500.00 |
      | Transport     | 700.00  |
      | Underholdning | 450.00  |
      | Shopping      | 1000.00 |

  Scenario: Show each category's percentage of the monthly total
    Given the selected month is "2026-08"
    When the user opens the monthly overview
    Then the monthly total is 4650.00 DKK
    And the chart shows these percentages rounded to the nearest whole percent:
      | category      | percentage |
      | Mad           | 54         |
      | Transport     | 15         |
      | Underholdning | 10         |
      | Shopping      | 21         |

  Scenario: Update the chart when another month is selected
    Given the selected month is "2026-08"
    And the monthly overview is open
    When the user selects month "2026-09"
    Then the chart contains these category totals:
      | category | amount |
      | Mad      | 300.00 |
    And the chart does not contain expenses dated in "2026-08"

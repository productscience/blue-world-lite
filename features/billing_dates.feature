Feature: Billing dates
  Scenario: _setup
    Given I switch to the user browser
      And I navigate to /logout

  Scenario Outline: See one year in advance
    Given I freeze time at <date>
     When I navigate to /billing-dates
     Then I see "<expected>" in ".invoicing-date"

    Examples:
     | date                | expected        |
     | 2016-07-17 14:59:59 | Sun 03 Jul 2016 |
     | 2016-07-17 15:00:00 | Sun 03 Jul 2016 |

  Scenario: _teardown
    Given I return to the current time

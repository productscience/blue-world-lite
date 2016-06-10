Feature: Dashboard

  Scenario: Visit dashboard when not signed in
    Given I'm using the user browser
     When I navigate to /accounts/profile
     Then I see "Not logged in" in "body"

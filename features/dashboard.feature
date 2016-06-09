Feature: Dashboard

  Scenario: Visit dashboard when not signed in
     When I navigate to /accounts/profile
     Then I see "Not logged in" in "body"

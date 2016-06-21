Feature: Dashboard

  Scenario: Visit dashboard when not signed in
    Given I'm using the user browser
      And I navigate to /logout
     When I navigate to /dashboard/
     Then I see "Not logged in" in "body"

Feature: Dashboard

  Scenario: Visit dashboard when not signed in
    Given I'm using the user browser
      And I navigate to /logout
     When I navigate to /dashboard/
     Then I see "Not logged in" in "body"

#   Scenario: I can logout from the dashbaord
#     Given I'm using the user browser
#       And I navigate to /dashboard/
#      When I follow the "Log out" link
#      Then the browser moves to /logout/
#      When I navigate to /dashboard/
#      Then I see "Not logged in" in "body"

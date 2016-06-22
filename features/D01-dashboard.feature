Feature: Dashboard

  Scenario: Visit dashboard when not signed in
    Given I'm using the user browser
      And I navigate to /logout
     When I navigate to /dashboard/
     Then I see "Not logged in" in "body"

  Scenario: I can logout from the dashbaord
    Given I create user "User D01", "user d01", "user_d01@example.com" with password "123123d01" and login
      And I navigate to /dashboard/
     When I follow the "Log out" link
     Then the browser moves to /
      And I see "You have signed out" in "ul"
     When I navigate to /dashboard/
     Then I see "Not logged in" in "body"

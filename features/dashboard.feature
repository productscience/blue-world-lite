Feature: Dashboard

  Scenario: Visit dashboard when not signed in
    Given I'm using the user browser
      And I create user "Dashboard", "dashboard", "dashboard@example.com" with password "123123ab"
      And I navigate to /logout
     When I navigate to /dashboard
     Then the browser moves to /login?next=/dashboard

  Scenario Outline: Dashboard Links
    Given I login with "dashboard@example.com" and "123123ab"
      And I navigate to /dashboard
     When I follow the "<link>" link
     Then the browser moves to <url>
      And I see "This functionality is not implemented yet" in "p"

   Examples: Dashboard links
     | link                    | url                                |
     | Change order            | /dashboard/change-order            |
     | Change collection point | /dashboard/change-collection-point |

  Scenario: I can logout from the dashbaord
    Given I navigate to /dashboard
     When I follow the "Log out" link
     Then the browser moves to /
      And I see "You have signed out" in "ul"
     When I navigate to /dashboard
     Then the browser moves to /login?next=/dashboard

  Scenario Outline: Protected dashboard URLs
     When I navigate to <url>
     Then the browser moves to /login?next=<url>

   Examples: Protected URLs
     | url                                |
     | /dashboard/change-order            |
     | /dashboard/change-collection-point |

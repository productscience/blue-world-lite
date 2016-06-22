Feature: Join - Cannot join if logged in

  Scenario: _setup
    Given I create user "Cannot Join If Logged In", "cannot-join-if-logged-in", "cannot-join-if-logged-in@example.com" with password "123123ab"
      And I login with "cannot-join-if-logged-in@example.com" and "123123ab"

  Scenario: Home redirects to dashbaord
     When I navigate to /
     Then the browser moves to /dashboard

  Scenario Outline: I can't visit any join pages now I've joined and am signed in
    Given I navigate to <url>
      And I see "You cannot join if you are already a signed in user" in "h3"
     When I follow the "visit the dashboard" link
     Then the browser moves to /dashboard

   Examples: Pages I can no longer access
     | url                    |
     | /join/choose-bags      |
     | /join/collection-point |
     | /join/login-details    |

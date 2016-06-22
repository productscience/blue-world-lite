Feature: Log in
  Scenario: Successful log in
    Given I switch to the user browser
      And I create user "User A03", "user a03", "user_a03@example.com" with password "123123a03"
      And I navigate to /login
      And I see "Log In" in "h1"
      And I type "user_a03@example.com" into "#id_login"
      And I type "123123a03" into "#id_password"
     When I click the "Log in" button
     Then the browser moves to /dashboard/

  Scenario: Can't access login when logged in
     When I navigate to /login
     Then the browser moves to /dashboard/

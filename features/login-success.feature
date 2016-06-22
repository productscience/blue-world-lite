Feature: Log in
  Scenario: Successful log in
    Given I switch to the user browser
      And I create user "Login Success", "login-success", "login-success@example.com" with password "123123ab"
      And I navigate to /login
      And I see "Log In" in "h1"
      And I type "login-success@example.com" into "#id_login"
      And I type "123123ab" into "#id_password"
     When I click the "Log in" button
     Then the browser moves to /dashboard

  Scenario: Visiting /login redirects to dashboard
     When I navigate to /login
     Then the browser moves to /dashboard

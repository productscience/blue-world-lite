Feature: Log in
  Scenario: Successful log in
    Given I switch to the user browser
      And I create a started user "Login Success", "login-success", "login-success@example.com" with password "123123ab"
      And I navigate to /login
      And I see "Log In" in "h1"
      And I type "login-success@example.com" into "#id_login"
      And I type "123123ab" into "#id_password"
     When I click the "Log in" button
     Then the browser moves to /dashboard

  Scenario: Visiting /login redirects to dashboard
     When I navigate to /login
     Then the browser moves to /dashboard

  Scenario: Visiting /logout redirects to /logged-out
     When I navigate to /logout
     Then the browser moves to /logged-out
      And I see "You have signed out." in "#messages"
      And I see "Logged Out" in "h1"
      And I see "Thanks for visiting." in "p"

  Scenario: Visiting /logged-out while logged in logs me out too
    Given I login with "login-success@example.com" and "123123ab"
     When I navigate to /logged-out
     Then I see "You have signed out." in "#messages"
      And I see "Logged Out" in "h1"
      And I see "Thanks for visiting." in "p"
     When I navigate to /dashboard
     Then the browser moves to /login?next=/dashboard

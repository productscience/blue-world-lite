Feature: Login - Can't continue until verified email

  Scenario: _setup
    Given I switch to the user browser
      And I navigate to /logout
      And I navigate to /
      And I click the "Join the scheme" button

  Scenario: Shown the verify email page
    Given I choose one large veg box to collect from the Old Fire Station
      And I clear any sent emails
      And the browser is still at /join/login-details
      And I type "login-unverified@example.com" into "#id_email"
      And I type "123123ab" into "#id_password1"
      And I type "Login Unverified" into "#id_full_name"
      And I type "login-unverified" into "#id_nickname"
      And I type "01234 567890" into "#id_mobile"
      And I click the "Sign Up" button
      And the browser moves to /confirm-email
      And I see "Verify Your E-mail Address" in "h1"
    Given I navigate to /logout
      And I navigate to /login
      And I type "login-unverified@example.com" into "#id_login"
      And I type "123123ab" into "#id_password"
     When I click the "Log in" button
     Then the browser moves to /confirm-email
      And I see "Verify Your E-mail Address" in "h1"
     When I navigate to /dashboard
     Then the browser moves to /login?next=/dashboard


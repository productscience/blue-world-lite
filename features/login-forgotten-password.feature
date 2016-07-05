Feature: Forgotten password
  Scenario: _setup
    Given I switch to the user browser
      And I create a started user "Forgotten Password", "forgotten-password", "forgotten-password@example.com" with password "123123ab"

  Scenario: Navigate to forgotten password
    Given I navigate to /login
     When I follow the "Forgot Password?" link
     Then the browser moves to /password/reset/

  Scenario: Non-existant email
    Given I type "not-a-real-email@example.com" into "#id_email"
     When I click the "Reset My Password" button
     Then the browser is still at /password/reset/
      And I see "The e-mail address is not assigned to any user account" in ".errorlist"

  Scenario: Success
    Given I clear any sent emails
      And I type "forgotten-password@example.com" into "#id_email"
     When I click the "Reset My Password" button
     Then the browser moves to /password/reset/done/
      And I see "We have sent you an e-mail. Please contact us if you do not receive it within a few minutes." in "p"
      And 1 email has been sent
      And I fetch the first sent email
      And the email is to "forgotten-password@example.com"
      And the email is from "no-reply@blueworld.example.com"
      And the email subject is "[BlueWorld] Password Reset E-mail"
      And I capture the value of "/password/reset/key/(.*)/" in the message to the "token" variable

      # And I switch to the admin browser
      # And I navigate to /admin/
      # And I follow the "Email confirmations" link
      # And I follow the "forgotten-password@example.com (forgotten-password)" link
      # And I capture the value of "#id_key" to the "key" variable

    Given I switch to the user browser
      And I navigate to the formatted url /password/reset/key/{token}/
      And I see "Change Password" in "h1"
    Given I type "123123bc" into "#id_password1"
      And I type "123123bc" into "#id_password2"
     When I click the "change password" button
     Then the browser moves to /password/reset/key/done/
      And I see "Password successfully changed." in "#messages"

    Given I navigate to /dashboard
     Then the browser moves to /login?next=/dashboard
      And I type "forgotten-password@example.com" into "#id_login"
      And I type "123123ab" into "#id_password"
     When I click the "Log in" button
     Then the browser moves to /login
     # Then the browser is still at /login?next=/dashboard
    Given I type "forgotten-password@example.com" into "#id_login"
      And I type "123123bc" into "#id_password"
     When I click the "Log in" button
     Then the browser moves to /dashboard


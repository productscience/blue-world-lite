Feature: Join - Verify Email Address Immediately

  Scenario: _setup
    Given I switch to the user browser
      And I navigate to /logout
      And I navigate to /
      And I click the "Join the scheme" button

  Scenario: Successfully join the scheme
    Given I choose one large veg box to collect from the Old Fire Station
      And I clear any sent emails
      And the browser is still at /join/login-details
      And I type "join-verify-immediately@example.com" into "#id_email"
      And I type "123123ab" into "#id_password1"
      And I type "Join Verify Immediately" into "#id_full_name"
      And I type "join-verify-immediately" into "#id_nickname"
      And I type "01234 567890" into "#id_mobile"
     When I click the "Sign Up" button
     Then the browser moves to /confirm-email
      And I see "Verify Your E-mail Address" in "h1"
      And 1 email has been sent
      And I fetch the first sent email
     # Should have stored the data here.
      And the email is to "join-verify-immediately@example.com"
      And the email is from "no-reply@blueworld.example.com"
      And the email subject is "[BlueWorld] Please Confirm Your E-mail Address"
    Given I'm using the admin browser
      And I login as a superuser
      And I follow the "Email confirmations" link
      And I follow the "join-verify-immediately@example.com (join-verify-immediately)" link
      And I capture the value of "#id_key" to the "key" variable
      And the formatted email body contains "http://localhost:8000/confirm-email/{key}/"
    Given I switch to the user browser
     When I navigate to the formatted url /confirm-email/{key}/
     Then I see "Confirm E-mail Address" in "h1"
      And I see "Please confirm that join-verify-immediately@example.com is an e-mail address for user join-verify-immediately." in "body"
     When I click the "Confirm" button
     Then the browser moves to /dashboard
      And I see "Set up Go Cardless" in "h1"
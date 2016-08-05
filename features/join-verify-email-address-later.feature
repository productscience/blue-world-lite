Feature: Join - Verify Email Address Later

  Scenario: _setup
    Given I switch to the user browser
      And I navigate to /logout
      And I navigate to /
      And I click the "Join the scheme" button

  Scenario: Successfully join the scheme after logging out
    Given I choose one large veg box to collect from the Old Fire Station
      And I clear any sent emails
      And the browser is still at /join/login-details
      And I type "join-verify-later@example.com" into "#id_email"
      And I type "123123ab" into "#id_password1"
      And I type "Join Verify Later" into "#id_full_name"
      And I type "join-verify-later" into "#id_nickname"
      And I type "01234 567890" into "#id_mobile"
     When I click the "Sign Up" button
     Then the browser moves to /confirm-email
      And I see "Verify Your E-mail Address" in "h1"
    Given I navigate to /logout

    Given 1 email has been sent
      And I fetch the first sent email
     # Should have stored the data here.
      And the email is to "join-verify-later@example.com"
      And the email is from "no-reply@blueworld.example.com"
      And the email subject is "[BlueWorld] Please Confirm Your E-mail Address"
      And I capture the value of "/confirm-email/(.*)/" in the message to the "key" variable
     When I navigate to the formatted url /confirm-email/{key}/
     Then I see "Confirm E-mail Address" in "h1"
      And I see "join-verify-later@example.com" in "body"
     When I click on ".confirm button"
     Then the browser moves to /dashboard/gocardless
      And I see "Set up Go Cardless" in "h1"

Feature: Change email
  Scenario: _setup
    Given I switch to the user browser
      And I create a started user "Email Changer", "email-changer", "email-changer@example.com" with password "123123ab"
      And I login with "email-changer@example.com" and "123123ab"

  Scenario: Navigate from Dashboard
    Given I navigate to /dashboard
     And I hover over "#navigation .your_account"
     When I follow the "E-mail Addresses" link in "#navigation"
     Then the browser moves to /email/
      And I see "E-mail Addresses" in "h1"

  Scenario: Existing email is present
    Given I navigate to /email/
     Then there is 1 "input[type='radio']" element in "form"
      And the value of "#email_radio_1" is "email-changer@example.com"
      And "#email_radio_1" is checked

  @chrome
  Scenario: Cannot remove primary email
     When I click the "Remove" button
     Then the alert says "Do you really want to remove the selected e-mail address?"
      And I cancel the alert
      And the browser is still at /email/
      And there is 1 "input[type='radio']" element in "form"
      And the value of "#email_radio_1" is "email-changer@example.com"
      And "#email_radio_1" is checked
     When I click the "Remove" button
     Then the alert says "Do you really want to remove the selected e-mail address?"
      And I accept the alert
     Then the browser is still at /email/
      And there is 1 "input[type='radio']" element in "form"
      And the value of "#email_radio_1" is "email-changer@example.com"
      And "#email_radio_1" is checked
      And I see "You cannot remove your primary e-mail address (email-changer@example.com)." in "#messages"


  Scenario: Add an email
    Given I switch to the admin browser
      And I login as a superuser
      And I navigate to /admin/auth/user/
     When I follow the "email-changer" link
     Then the value of "#id_email" is "email-changer@example.com"

    Given I clear any sent emails
      And I switch to the user browser
      And I navigate to /email/
      And I type "email-changer-2@example.com" into "#id_email"
     When I click the "Add E-mail" button
     Then the browser is still at /email/
      And I see "Confirmation e-mail sent to email-changer-2@example.com." in "#messages"
      And 1 email has been sent
      And I fetch the first sent email
      And the email is to "email-changer-2@example.com"
      And the email is from "no-reply@blueworld.example.com"
      And the email subject is "[BlueWorld] Please Confirm Your E-mail Address"

      And I switch to the admin browser
      And I navigate to /admin/
      And I follow the "Email confirmations" link
      And I follow the "email-changer-2@example.com (email-changer)" link
      And I capture the value of "#id_key" to the "key" variable

    Given I switch to the user browser
      And I navigate to the formatted url /confirm-email/{key}/
      And I see "Confirm E-mail Address" in "h1"
     When I click the "Confirm" button
     Then the browser moves to /dashboard
      And I see "You have confirmed email-changer-2@example.com." in "#messages"

    Given I navigate to /email/
      #And I click the "email-changer-2@example.com" label
      # Label selection isn't working, the new email comes first so click it that way
      And I click on "#email_radio_1"
     When I click the "Make Primary" button
     Then the browser is still at /email/
      And I see "Primary e-mail address set." in "#messages"

    Given I switch to the admin browser
      And I navigate to /admin/auth/user/
     When I follow the "email-changer" link
     Then the value of "#id_email" is "email-changer-2@example.com"

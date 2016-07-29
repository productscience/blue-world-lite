Feature: Change Password
  Scenario: _setup
    Given I switch to the user browser
      And I create a started user "Password Changer", "password-changer", "password-changer@example.com" with password "123123ab"
      And I login with "password-changer@example.com" and "123123ab"

  Scenario: Can navigate from dashbaord
    Given I navigate to /dashboard
     And I hover over "#navigation .your_account"
     When I follow the "Change Password" link in "#navigation"
     Then the browser moves to /password/change/
      And I see "Change Password" in "h1"

  Scenario: Wrong current password
    Given I type "wrong" into "#id_oldpassword"
      And I type "123123bc" into "#id_password1"
      And I type "123123bc" into "#id_password2"
     When I click the "Change Password" button
     Then the browser is still at /password/change/
      And I see "Please type your current password." in ".errorlist"

  Scenario: Wrong new password
    Given I type "123123ab" into "#id_oldpassword"
      And I type "123123bc" into "#id_password1"
      And I type "123123wrong" into "#id_password2"
     When I click the "Change Password" button
     Then the browser is still at /password/change/
      And I see "You must type the same password each time." in ".errorlist"

  Scenario: Success
    Given I type "123123ab" into "#id_oldpassword"
      And I type "123123bc" into "#id_password1"
      And I type "123123bc" into "#id_password2"
     When I click the "Change Password" button
     Then the browser is still at /password/change/
      And I see "Password successfully changed." in "#messages"

  Scenario: Can't login with old password
    Given I navigate to /logout
      And I navigate to /login
      And I type "password-changer@example.com" into "#id_login"
      And I type "123123ab" into "#id_password"
     When I click the "Log in" button
     Then the browser is still at /login

  Scenario: Can login with new password
    Given I type "password-changer@example.com" into "#id_login"
      And I type "123123bc" into "#id_password"
     When I click the "Log in" button
     Then the browser moves to /dashboard

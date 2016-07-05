Feature: Inactive Account
  Scenario: _setup
    Given I switch to the user browser
      And I create a started user "Inactive Account", "inactive-account", "inactive-account@example.com" with password "123123ab"

  Scenario: Inactivate account
    Given I switch to the admin browser
      And I login as a superuser
      And I navigate to /admin/auth/user
      And I follow the "inactive-account" link
      And I click on "#id_is_active"
      And I click the "Save" button

    Given I switch to the user browser
      And I navigate to /logout
      And I navigate to /login
      And I see "Log In" in "h1"
      And I type "inactive-account@example.com" into "#id_login"
      And I type "123123ab" into "#id_password"
     When I click the "Log in" button
     Then the browser moves to /inactive/
      And I see "Account Inactive" in "h1"
    Given I navigate to /dashboard
     Then the browser moves to /login?next=/dashboard

  Scenario: Re-activate account
    Given I switch to the admin browser
      And I follow the "inactive-account" link
      And I click on "#id_is_active"
      And I click the "Save" button

    Given I switch to the user browser
     When I login with "inactive-account@example.com" and "123123ab"
     Then the browser moves to /dashboard

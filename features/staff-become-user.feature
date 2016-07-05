Feature: Become user
  Scenario: _setup
    Given I switch to the user browser
      And I navigate to /logout
      And I navigate to /admin/logout/
      And I create a started user "Becomer", "becomer", "becomer@example.com" with password "123123ab"
      And I login as a member of staff

  Scenario: Become Becomer
    Given I navigate to /admin/join/customer/?q=Becomer
     When I click the "Become Becomer" button
     Then the browser moves to /dashboard
      And I see "Dashboard" in "h1"
      And I see "You are currently working on behalf of Becomer" in "#hijack-notification"

  Scenario: Can't access the admin as leaver
     When I navigate to /admin/
     Then the browser moves to /admin/login/?next=/admin/

  Scenario: Release leaver
    Given I navigate to /dashboard
     When I click the "Release" button
     Then the browser moves to /admin/
      And I see "staff" in "#user-tools"

  Scenario: _teardown
    Given I navigate to /admin/logout

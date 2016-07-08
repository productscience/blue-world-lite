Feature: Collection Point Screen

   Note: If the user chooses a collection point which then becomes deactivated
   *after* they clicked next, it will probably still be their chosen collection
   point at the time they create their account. This is controlled by
   SESSION_COOKIE_AGE in the blueworld/settings.py file.

  Scenario: _setup
    Given I switch to the user browser
      And I navigate to /logout
      And I navigate to /
      And I click the "Join the scheme" button

  Scenario: Can't continue to login details if I haven't chosen a collection point
    Given the browser is still at /join/choose-bags
      And I type "1" into "#id_form-2-quantity"
      And I click the "Next" button
      And the browser moves to /join/collection-point
      And I see "Where do you want to pick up your bag from?" in "h3"
     When I click the "Next" button
     Then the browser is still at /join/collection-point
      And I see "This field is required" in "#errors"

  Scenario: Logo links to home screen
    Given the browser is still at /join/collection-point
     When I follow the "Members Home" link
     Then the browser moves to /


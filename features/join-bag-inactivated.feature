Feature: Join - Bag type inactivated

  Scenario: _setup
    Given I switch to the user browser
      And I navigate to /logout
      And I navigate to /
      And I click the "Join the scheme" button

  Scenario: Successfully join the scheme with deactivated bag
    Given I choose one large veg box to collect from the Old Fire Station

    Given I switch to the admin browser
      And I login as a member of staff
      And I navigate to /admin/join/bagtype
      And I follow the "Large veg" link
      And I click on "#id_active"
      And I click the "Save" button

    Given I switch to the user browser
      And I type "join-verify-immediately@example.com" into "#id_email"
      And I type "123123ab" into "#id_password1"
      And I type "Join Verify Immediately" into "#id_full_name"
      And I type "join-verify-immediately" into "#id_nickname"
      And I type "01234 567890" into "#id_mobile"
     When I click the "Sign Up" button
     Then the browser is still at /join/login-details
      And I see "Not all of your bag choices are available" in "h3"
      And I follow the "go back and update your order" link
      And the browser moves to /join/choose-bags

    Given I switch to the admin browser
      And I navigate to /admin/join/bagtype
      And I follow the "Large veg" link
      And I click on "#id_active"
      And I click the "Save" button

      And I switch to the user browser

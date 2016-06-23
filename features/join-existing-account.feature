Feature: Join - Existing Account

  Scenario: Can't join the scheme with the same email as an existing account
    Given I create an email verified user "Join Existing Account", "join-existing-account", "join-existing-account@example.com" with password "123123ab"
      And I choose one large veg box to collect from the Old Fire Station
      And the browser is still at /join/login-details
      And I type "join-existing-account@example.com" into "#id_email"
      And I type "123123otherpassword" into "#id_password1"
      And I type "Another Name" into "#id_full_name"
      And I type "Another Nickname" into "#id_nickname"
     When I click the "Sign Up" button
     Then the browser is still at /join/login-details
     # XXX And

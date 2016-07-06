Feature: Change Collection Point

  Scenario: _setup
    Given I'm using the user browser
      And I create a started user "Change Collection Point", "change-collection-point", "change-collection-point@example.com" with password "123123ab"
      And I login with "change-collection-point@example.com" and "123123ab"
      And I follow the "Change Collection Point" link

  Scenario: Make no changes
     When I click the "Confirm" button
     Then the browser is still at /dashboard/change-collection-point
      And I see "You haven't made any changes to your collection point." in "#messages"

  Scenario: Cancel
     When I click the "Cancel" button
     Then the browser moves to /dashboard
      And I see "Your collection point has not been changed" in "#messages"

  Scenario: Change collection point XXX
    Given I navigate to /dashboard/change-collection-point
      And I click the "St John of Jerusalem Church" label
     When I click the "Confirm" button
     Then the browser moves to /dashboard
      And I see "Your collection point has been updated successfully" in "#messages"
      And I see "St John of Jerusalem Church" in "#collection-point"

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

  Scenario: Change collection point
    Given I navigate to /dashboard/change-collection-point
      And I click the "St John of Jerusalem Church" label
     When I click the "Confirm" button
     Then the browser moves to /dashboard
      And I see "Your collection point has been updated successfully" in "#messages"
      And I see "St John of Jerusalem Church" in "#collection-point"

  Scenario: Current collection point is no longer active, show a warning
    Given I switch to the admin browser
      And I navigate to /admin/join/collectionpoint
      And I follow the "St John of Jerusalem Church" link
      And I click on "#id_active"
      And I click the "Save" button

      And I switch to the user browser
      And I navigate to /dashboard/change-collection-point
      And I see "Please be aware that St John of Jerusalem Church is currently full or closing down so if you switch to another collection point you won't be able to change back to St John of Jerusalem Church afterwards." in "#collection-point-not-active-warning"
      And I click the "Mother Earth (Albion Rd)" label
     When I click the "Confirm" button
     Then the browser moves to /dashboard
      And I see "Your collection point has been updated successfully" in "#messages"
      And I see "Mother Earth (Albion Rd)" in "#collection-point"

  Scenario: Newly chosen collection point is no longer active, so we the old one is shown again
    Given I navigate to /dashboard/change-collection-point
      And I click the "Springfield" label
      And I switch to the admin browser
      And I navigate to /admin/join/collectionpoint
      And I follow the "Springfield" link
      And I click on "#id_active"
      And I click the "Save" button

      And I switch to the user browser
      And I click the "Confirm" button
      And the browser is still at /dashboard/change-collection-point
      And I see "That choice is not one of the available choices." in ".errorlist .errorlist li"
     When I click the "Cancel" button
     Then I see "Mother Earth (Albion Rd)" in "#collection-point"

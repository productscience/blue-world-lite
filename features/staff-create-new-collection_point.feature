Feature: Create new collection point
  Scenario: _setup
    Given I switch to the user browser
      And I login as a member of staff

  Scenario: Can navigate to New collection point form 2
    Given I navigate to /admin
      And I follow the "Collection points" link
      And the browser moves to /admin/join/collectionpoint/
     When I follow the "ADD COLLECTION POINT" link
     Then the browser moves to /admin/join/collectionpoint/add/
      And I see "Add collection point" in "#content h1"

  Scenario: Error when adding a new collection point with an existing name
    Given I type "The Old Fire Station" into "#id_name"
     When I click the "Save" button
     Then the browser is still at /admin/join/collectionpoint/add/
      And I see "Please correct the error below." in "p.errornote"

  Scenario: Successfully add new collection point
    Given I type "New Collection Point" into "#id_name"
     When I click the "Save" button
     Then the browser moves to /admin/join/collectionpoint/
      And I see "added successfully" in ".messagelist .success"
      And I see "New Collection Point" in "#changelist"

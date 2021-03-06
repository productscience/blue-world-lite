Feature: Staff bag type admin
  Scenario: _setup
    Given I switch to the user browser
      And I login as a member of staff

  Scenario: Can navigate to New bag type form
    Given I navigate to /admin
      And I follow the "Bag types" link
      And the browser moves to /admin/join/bagtype/
     When I follow the "ADD BAG TYPE" link
     Then the browser moves to /admin/join/bagtype/add/
      And I see "Add bag type" in "#content h1"

  Scenario: Error when adding a new bag type with an existing name
    Given I type "Large veg" into "#id_name"
      And I type "12.56" into "#id_weekly_cost"
     When I click the "Save" button
     Then the browser is still at /admin/join/bagtype/add/
      And I see "Please correct the error below." in "p.errornote"

  Scenario: Error when not entering a cost
    Given I navigate to /admin/join/bagtype/
      And I follow the "ADD BAG TYPE" link
      And I type "New Bag Type" into "#id_name"
     When I click the "Save" button
     Then the browser is still at /admin/join/bagtype/add/
      And I see "Please correct the error below." in "p.errornote"

  Scenario: Successfully add new bag type
    Given I type "New Bag Type" into "#id_name"
      And I type "12.56" into "#id_weekly_cost"
     When I click the "Save" button
     Then the browser moves to /admin/join/bagtype/
      And I see "added successfully" in ".messagelist .success"
      And I see "New Bag Type" in "#changelist"
     When I follow the "New Bag Type" link
     Then the value of "#id_weekly_cost" is "12.56"

  Scenario Outline: Cannot use an existing name
    Given I navigate to /admin/join/bagtype/
      And I follow the "New Bag Type" link
      And I capture the value of "/admin/join/bagtype/(.*)/change/" in the URL to the "pk" variable
      And I type "<name>" into "#id_name"
      And I type "<weekly_cost>" into "#id_weekly_cost"
     When I click the "Save" button
     Then the browser is at the formatted URL /admin/join/bagtype/{pk}/change/
      And I see "Please correct the error below." in "p.errornote"

   Examples: Error data
     | name         | weekly_cost |
     | Large veg    | 12.56       |
     | New Bag Type |             |
     | New Bag Type | 12.5678     |
     | New Bag Type | -12.56      |

  Scenario: Successfully edit bag type name
    Given I navigate to /admin/join/bagtype/
      And I follow the "New Bag Type" link
      And I type "New Bag Type Edited" into "#id_name"
     When I click the "Save" button
     Then the browser moves to /admin/join/bagtype/
      And I see "changed successfully" in ".messagelist .success"
      And I see "New Bag Type Edited" in "#changelist"

  Scenario: _teardown
    Given I navigate to /admin/logout/

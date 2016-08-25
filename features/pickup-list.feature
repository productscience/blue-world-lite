Feature: Pick up List
  Scenario: _setup
    Given I switch to the user browser
      And I login as a member of staff

  Scenario: Choose all collection points
    Given I navigate to /admin/join/collectionpoint/
      And I click on "#action-toggle"
      And I choose "Generated pick up list for selected collection points" from ".actions select"
     When I click the "Go" button
     Then the browser is still at /admin/join/collectionpoint/
      And I see "Choose date for pick up lists" in "#content h1"

    Given I type "2016-07 4" into "#id_billing_week"
     When I click the "Generate" button
     Then the browser is still at /admin/join/collectionpoint/
      And I see "Billing Week 4, July 2016 Pick Up Lists" in "h1"

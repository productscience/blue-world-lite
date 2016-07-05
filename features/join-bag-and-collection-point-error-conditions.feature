Feature: Join - Bag and Collection Point Error Conditions

  Scenario: _setup
    Given I switch to the user browser
      And I navigate to /logout
      And I navigate to /
      And I click the "Join the scheme" button

  Scenario: Can't navigate to collection point if I haven't already selected at least one bag
    Given I navigate to /join/collection-point
      And I see "You have not chosen any bags" in "h3"
     When I follow the "go back and choose at least one" link
     Then the browser moves to /join/choose-bags
      And I see "Which bags do you want to pick up each week?" in "h3"

  Scenario: Can't navigate to login details if I haven't already selected at least one bag
    Given I navigate to /join/login-details
      And I see "You have not chosen any bags" in "h3"
     When I follow the "go back and choose at least one" link
     Then the browser moves to /join/choose-bags
      And I see "Which bags do you want to pick up each week?" in "h3"

  Scenario: Can't navigate to login details if I haven't already chosen a collection point
    Given I navigate to /join/choose-bags
      And I see "Which bags do you want to pick up each week?" in "h3"
      And I type "1" into "#id_form-0-quantity"
      And I click the "Next" button
      And the browser moves to /join/collection-point
      And I navigate to /join/login-details
     Then I see "You must choose a collection point" in "h3"
     When I follow the "go back and choose one" link
     Then the browser moves to /join/collection-point
      And I see "Where do you want to pick up your bag from?" in "h3"

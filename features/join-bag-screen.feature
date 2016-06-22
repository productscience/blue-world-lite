Feature: Bag Screen

  Scenario: _setup
    Given I switch to the user browser
      And I navigate to /logout
      And I navigate to /
      And I click the "Join the scheme" button

  Scenario: Can't continue to collection point if I don't have at least one bag
    Given I navigate to /join/choose-bags
      And I see "Which bags do you want to pick up each week?" in "h3"
     When I click the "Next" button
     Then the browser is still at /join/choose-bags
      And I see "Please choose at least one bag to order" in "#errors"

  Scenario: Can't continue to collection point if I enter an invalid value
    Given the browser is still at /join/choose-bags
      And I see "Which bags do you want to pick up each week?" in "h3"
      And I type "-1" into "#id_form-2-quantity"
     When I click the "Next" button
     Then the browser is still at /join/choose-bags
      And I see "Ensure this value is greater than or equal to 0." in "tr.error > td"

  Scenario: Logo links to home screen
    Given the browser is still at /join/choose-bags
     When I follow the "Members Home" link
     Then the browser moves to /

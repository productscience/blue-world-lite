Feature: Join - Support Going Back

  Scenario: _setup
    Given I switch to the user browser
      And I navigate to /logout
      And I navigate to /
      And I click the "Join the scheme" button

  Scenario: /join redirects to start the process
    Given I'm using the user browser
     When I navigate to /join
     Then the browser moves to /join/choose-bags
     When I navigate to /join/
     Then the browser moves to /join/choose-bags

  Scenario: Complete choose bags and follow the back link, your choice is still there
    Given I navigate to /join/choose-bags
      And I see "Which bags do you want to collect each week?" in "h3"
      # One of the inputs from the test data is active=False so is excluded
      And there are 3 "input" elements in "form"
      And the value of "#id_form-1-quantity" is "0"
      And the value of "#id_form-0-quantity" is "0"
      And I type "1" into "#id_form-0-quantity"
      And I click the "Next" button
      And the browser moves to /join/collection-point
    Given I navigate to /join/choose-bags
      And the value of "#id_form-1-quantity" is "0"
      And the value of "#id_form-0-quantity" is "1"
      And there are 3 "input" elements in "form"
      And I type "2" into "#id_form-0-quantity"
     When I click the "Next" button
     Then the browser moves to /join/collection-point
    Given I navigate to /join/choose-bags
      And the value of "#id_form-1-quantity" is "0"
      And the value of "#id_form-0-quantity" is "2"
      And there are 3 "input" elements in "form"
     When I click the "Next" button
     Then the browser moves to /join/collection-point

  Scenario: Reset bag choices when you click the "Join the scheme" button again
    Given I navigate to /
     When I click the "Join the scheme" button
     Then the browser moves to /join/choose-bags
      And the value of "#id_form-1-quantity" is "0"
      And the value of "#id_form-0-quantity" is "0"

  Scenario: Complete choose bags and collection point, both choices are still there when you navigate back to them
    Given I navigate to /join/choose-bags
      And I see "Which bags do you want to collect each week?" in "h3"
      # One of the inputs from the test data is active=False so is excluded
      And there are 3 "input" elements in "form"
      And the value of "#id_form-1-quantity" is "0"
      And the value of "#id_form-0-quantity" is "0"
      And I type "1" into "#id_form-0-quantity"
      And I click the "Next" button
      And the browser moves to /join/collection-point
    Given I navigate to /join/choose-bags
      And the value of "#id_form-1-quantity" is "0"
      And the value of "#id_form-0-quantity" is "1"
      And there are 3 "input" elements in "form"
      And I type "2" into "#id_form-0-quantity"
     When I click the "Next" button
     Then the browser moves to /join/collection-point
    Given I navigate to /join/choose-bags
      And the value of "#id_form-1-quantity" is "0"
      And the value of "#id_form-0-quantity" is "2"
      And there are 3 "input" elements in "form"
     When I click the "Next" button
     Then the browser moves to /join/collection-point
      And I see "Where do you want to collect your bag from?" in "h3"
      # One of the inputs from the test data is active=False so is excluded
      And there are 4 "input" elements in "form"
      And there are 0 "input[selected]" elements in "form"
      # Springfield has no location entered so has no <small> tag
      And I click the "The Old Fire Station" label
     When I click the "Next" button
     Then the browser moves to /join/login-details
      And I see "Sign Up" in "h1"
    Given I navigate to /join/choose-bags
     Then the value of "#id_form-1-quantity" is "0"
      And the value of "#id_form-0-quantity" is "2"
      And there are 3 "input" elements in "form"
     When I navigate to /join/collection-point
     Then there are 4 "input" elements in "form"
      And there is 1 "input[selected]" element in "form"
      And the value of "input[name=collection_point]" is "1"

  Scenario: Reset bag and collection point choices when you click the "Join the scheme" button again
    Given I navigate to /
     When I click the "Join the scheme" button
     Then the browser moves to /join/choose-bags
      And the value of "#id_form-1-quantity" is "0"
      And the value of "#id_form-0-quantity" is "0"
     When I navigate to /join/collection-point
      And I see "You have not chosen any bags" in "h3"
    Given I navigate to /join/choose-bags
      And I type "1" into "#id_form-0-quantity"
     When I click the "Next" button
     Then the browser moves to /join/collection-point
      And there are 0 "input[selected]" elements in "form"

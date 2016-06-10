Feature: Home screen

  Scenario: Visit the homepage and choose "Join the scheme"
    Given I'm using the user browser
      And I navigate to /
     When I click the "Join the scheme" button
     Then the browser moves to /join/choose-bags/
      And I see "Which bags do you want to pick up each week?" in "h1"

  Scenario: Visit the homepage and choose "Login"
    Given I navigate to /
     When I click the "Login" button
     Then the browser moves to /account/login/
      And I see "Sign In" in "h1"

  Scenario: Follow the "Staff Login" link
    Given I navigate to /
     When I follow the "Staff Login" link
     Then the browser moves to /admin/login/

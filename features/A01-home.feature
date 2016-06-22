Feature: Home screen

  Scenario: Logo links to home
    Given I'm using the user browser
      And I navigate to /
     When I follow the "Members Home" link
     Then the browser is still at /

  Scenario: Visit the homepage and choose "Join the scheme"
    Given I'm using the user browser
      And I navigate to /
     When I click the "Join the scheme" button
     Then the browser moves to /join/choose-bags/
      And I see "Which bags do you want to pick up each week?" in "h3"

  Scenario: Visit the homepage and choose "Login"
    Given I navigate to /
     When I click the "Login" button
     Then the browser moves to /login/
      And I see "Log In" in "h1"

  Scenario: Follow the "Staff Login" link
    Given I navigate to /
     When I follow the "Staff Login" link
     Then the browser moves to /admin/login/

Feature: Homepage

  Scenario: Visit homepage
    Given I'm using the user browser
     When I navigate to /
     Then I see "Login" in "body"
      And I see "Register" in "body"
      And I see "Staff Login" in "body"

  Scenario: Follow the "Login" link
    Given I navigate to /
     When I follow the "Login" link
     Then the browser moves to /accounts/login/

  Scenario: Follow the "Staff Login" link
    Given I navigate to /
     When I follow the "Staff Login" link
     Then the browser moves to /admin/login/?next=/admin/

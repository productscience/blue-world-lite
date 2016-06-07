Feature: Homepage

  Scenario: Visit homepage
     When I navigate to /
     Then I see "Login" within "body"
      And I see "Register" within "body"
      And I see "Staff Login" within "body"

  Scenario: Follow the "Login" link
     Given I navigate to /
     When I follow the "Login" link
     Then the browser moves to /accounts/login/

  Scenario: Follow the "Staff Login" link
     Given I navigate to /
     When I follow the "Staff Login" link
     Then the browser moves to /admin/login/?next=/admin/

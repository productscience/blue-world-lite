Feature: User Sign in

  Scenario: Visit sign in 
    Given I navigate to /accounts/login/
      And I see "Sign In" within "h1"
      And I see "Login" within "body"
      And I see "Password" within "body"
      And I type "test_user1" into "#id_login"
      And I type "test_password1" into "#id_password"
   #  When I click the "Sign In" button
   #  Then the browser moves to /accounts/profile
   #   And I see "Dashboard" within "body"


Feature: Staff login

   Scenario: Log into Django Admin
     Given I'm using the user browser
       And I navigate to /admin
       And the browser moves to /admin/login/?next=/admin/
       And I see "Django administration" in "h1"
       And I see "Username" in "body"
       And I see "Password" in "body"
       And I type "superuser" into "#id_username"
       And I type "123123ab" into "#id_password"
      When I click the "Log in" button
      Then the browser moves to /admin/
       And I see "superuser" in "#user-tools"


   Scenario: Log into Django Admin
     Given I'm using the admin browser
       And I navigate to /admin
       And the browser moves to /admin/login/?next=/admin/
     #  And I see "Django administration" in "h1"
     #  And I see "Username" in "body"
     #  And I see "Password" in "body"
     #  And I type "superuser" into "#id_username"
     #  And I type "123123ab" into "#id_password"
     # When I click the "Log in" button
     # Then the browser moves to /admin/
     #  And I see "superuser" in "#user-tools"

   Scenario: Logout
     Given I'm using the user browser
      When I navigate to /admin/logout/
      Then I see "Thanks for spending some quality time with the Web site today." in "body"
      When I navigate to /admin
      Then the browser moves to /admin/login/?next=/admin/

# Feature: User Log In
# 
#   Scenario: Visit log in page
#     Given I navigate to /accounts/login/
#       And I see "Sign In" within "h1"
#       And I see "Login" within "body"
#       And I see "Password" within "body"
#       And I type "t" into "#id_login"
#       And I type "test_password1" into "#id_password"
#      When I click the "Sign In" button
#      Then the browser moves to /accounts/profile
#       And I see "Dashboard" within "body"


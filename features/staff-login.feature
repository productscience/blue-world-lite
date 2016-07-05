Feature: Staff login

  Scenario: Log into Django Admin
    Given I'm using the user browser
      And I navigate to /logout
      And I switch to the admin browser
      And I navigate to /logout
      And I switch to the user browser
      And I navigate to /admin/
      And I login as a member of staff

  Scenario: Admin browser is still logged out
    Given I'm using the admin browser
      And I navigate to /admin/
      And the browser moves to /admin/login/?next=/admin/

  Scenario: Visit home page
    Given I'm using the user browser
     When I navigate to /
     Then the browser moves to /admin/

  Scenario Outline: Can't access dashboard as staff
     When I navigate to <url>
     Then I see "Staff don't have a dashboard" in "h1"

   Examples: Customer-only URLs
     | url                                |
     | /dashboard                         |
     | /dashboard/change-order            |
     | /dashboard/change-collection-point |
     | /dashboard/bank-details            |
     | /dashboard/leave                   |
     | /go-cardless-callback              |

  Scenario: Logout
    Given I'm using the user browser
     When I navigate to /admin/logout/
     Then I see "Thanks for spending some quality time with the Web site today." in "body"
     When I navigate to /admin
     Then the browser moves to /admin/login/?next=/admin/

  Scenario: Can't login as a normal user
    Given I create a started user "Non-Staff User", "non-staff-user", "non-staff-user@example.com" with password "123123ab"
      And I login with "non-staff-user@example.com" and "123123ab"
      And I navigate to /admin/
      And I type "non-staff-user" into "#id_username"
      And I type "123123ab" into "#id_password"
     When I click the "Log in" button
     Then the browser is still at /admin/login/?next=/admin/
      And I see "Please enter the correct username and password for a staff account. Note that both fields may be case-sensitive." in ".errornote"

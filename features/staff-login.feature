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

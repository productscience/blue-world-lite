Feature: Dashboard

  Scenario: Visit dashboard when not signed in
    Given I'm using the user browser
      And I create a started user "Dashboard", "dashboard", "dashboard@example.com" with password "123123ab"
     When I navigate to /dashboard
     Then the browser moves to /login?next=/dashboard

  Scenario Outline: Dashboard Links
    Given I login with "dashboard@example.com" and "123123ab"
      And I navigate to /dashboard
     When I follow the "<link>" link
     Then the browser moves to <url>
      And I see "<expected>" in "p"

   Examples: Dashboard links
     | link                    | url                                | expected                                         |
     | Change Order            | /dashboard/change-order            | Which bags do you want to pick up each week?     |
     | Change Collection Point | /dashboard/change-collection-point | Where do you want to pick up from?               |
     | Bank Details            | /dashboard/bank-details            | change your bank direct debit details            |
     | Leave                   | /dashboard/leave                   | tell us why you have decided to leave the scheme |
     | Order History           | /dashboard/order-history           | This functionality is not implemented yet        |

  Scenario: I can logout from the dashbaord
    Given I navigate to /dashboard
     When I follow the "Log Out" link
     Then the browser moves to /logged-out
      And I see "You have signed out" in "#messages"
     When I navigate to /dashboard
     Then the browser moves to /login?next=/dashboard

  Scenario Outline: Protected dashboard URLs from logged out users
    Given I navigate to /logout
     When I navigate to <url>
     Then the browser moves to /login?next=<url>

   Examples: Protected URLs
     | url                                |
     | /dashboard                         |
     | /dashboard/change-order            |
     | /dashboard/change-collection-point |
     | /dashboard/bank-details            |
     | /dashboard/leave                   |
     | /dashboard/order-history           |
     | /go-cardless-callback              |

  Scenario: Create a user without GoCardless
    Given I'm using the user browser
      And I create an email verified user "Dashboard GoCardless", "dashboard-gocardless", "dashboard-gocardless@example.com" with password "123123ab"
      And I login with "dashboard-gocardless@example.com" and "123123ab"

  Scenario Outline: Protected dashboard URLs from users who haven't set up GoCardless
     When I navigate to <url>
     Then I see "Set up Go Cardless" in "h1"

   Examples: Pages that show the set up gocardless page
     | url                                |
     | /dashboard                         |
     | /dashboard/change-order            |
     | /dashboard/change-collection-point |
     | /dashboard/bank-details            |
     | /dashboard/leave                   |
     | /dashboard/order-history           |

   #  | /go-cardless-callback              |

   Scenario: I set up GoCardless
     Given I navigate to /dashboard
      When I follow the "Skip" link
      Then I see "Successfully set up Go Cardless" in "#messages"
       And I see "Dashboard" in "h1"

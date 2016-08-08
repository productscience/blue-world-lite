Feature: Dashboard

  Scenario: _setup
    Given I'm using the user browser
      And I create a started user "Dashboard", "dashboard", "dashboard@example.com" with password "123123ab"

  Scenario: Visit dashboard when not signed in
     When I navigate to /dashboard
     Then the browser moves to /login?next=/dashboard
      And I login with "dashboard@example.com" and "123123ab"

  Scenario Outline: Dashboard Links
    Given I navigate to /dashboard
     And I hover over "<selector>"
     When I follow the "<link>" link in "#navigation"
     Then the browser moves to <url>
      And I see "<expected>" in "p"

   Examples: Dashboard links
     | link                    | selector                  | url                                | expected                                  |
     | Change Order            | #navigation .your_order   | /dashboard/change-order            | Your current order is                     |
     | Change Collection Point | #navigation .your_order   | /dashboard/change-collection-point | Your current collection point is          |
     | Bank Details            | #navigation .your_account | /dashboard/bank-details            | change your bank direct debit details     |
     | Leave                   | #navigation .your_order   | /dashboard/leave                   | We're sorry to see you go                 |
     | Order History           | #navigation .your_order   | /dashboard/order-history           | Your account was created on               |
     | Billing History         | #navigation .your_order   | /dashboard/billing-history         | Your payments                             |

  Scenario: Can't get the callback if you have completed GoCardless
    Given I'm using the user browser
      And I login with "dashboard@example.com" and "123123ab"
     When I navigate to /gocardless-callback
     Then I see "Go Cardless is Already Set Up" in "h1"

  Scenario: I can logout from the dashbaord
    Given I navigate to /dashboard
     And I hover over "#navigation .your_account"
     When I follow the "Log Out" link in "#navigation"
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
     | /dashboard/gocardless              |
     | /dashboard/change-order            |
     | /dashboard/change-collection-point |
     | /dashboard/bank-details            |
     | /dashboard/leave                   |
     | /dashboard/order-history           |
     | /dashboard/billing-history         |
     | /gocardless-callback               |

  Scenario: Create a user without GoCardless
    Given I'm using the user browser
      And I create an email verified user "Dashboard GoCardless", "dashboard-gocardless", "dashboard-gocardless@example.com" with password "123123ab"
      And I login with "dashboard-gocardless@example.com" and "123123ab" without GoCardless

  Scenario Outline: Protected dashboard URLs from users who haven't set up GoCardless
     When I navigate to <url>
     Then I see "Set up Go Cardless" in "h1"

   Examples: Pages that show the set up gocardless page
     | url                                |
     | /dashboard                         |
     | /dashboard/gocardless              |
     | /dashboard/change-order            |
     | /dashboard/change-collection-point |
     | /dashboard/bank-details            |
     | /dashboard/leave                   |
     | /dashboard/order-history           |
     | /dashboard/billing-history         |

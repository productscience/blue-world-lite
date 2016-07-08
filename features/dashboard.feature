Feature: Dashboard

  Scenario: _setup
    Given I'm using the user browser
      And I create a started user "Dashboard", "dashboard", "dashboard@example.com" with password "123123ab"

  Scenario: Visit dashboard when not signed in
     When I navigate to /dashboard
     Then the browser moves to /login?next=/dashboard

  Scenario Outline: Dashboard information after the last collection but before the deadline date
    # Need to freeze time first, otherwise you get logged out because of the session time of 20 mins
    Given I freeze time at <date>
      And I login with "dashboard@example.com" and "123123ab"
     When I navigate to /dashboard
     Then I see "Wed 20 July" in "#collection-date"
      And I see "You can make changes that affect your next collection any time before" in "#deadline-date-message"
      And I see "Sun 17 July 3:00 p.m." in "#deadline-date"

   # 13th is a Wednesday
   # 17th is a Sunday
   Examples: Times where you can make changes for the next collection
     | date                |
     | 2016-07-13 12:00:00 |
     | 2016-07-17 14:59:59 |

  Scenario Outline: Dashboard information after the deadline date but before the next collection
    Given I freeze time at 2016-07-17 15:00:00
      And I login with "dashboard@example.com" and "123123ab"
     When I navigate to /dashboard
     Then I see "Wed 20 July" in "#collection-date"
      And I see "You are too late for making changes for your next collection" in "#deadline-date-message"

   # 17th is a Sunday
   # 20th is a Wednesday
   Examples: Times when changes you make affect the collection after the next one
     | date                |
     | 2016-07-17 15:00:00 |
     | 2016-07-20 11:59:59 |

  Scenario: Unfrezee time
    Given I return to the current time
      And I login with "dashboard@example.com" and "123123ab"

  Scenario Outline: Dashboard Links
    Given I navigate to /dashboard
     When I follow the "<link>" link
     Then the browser moves to <url>
      And I see "<expected>" in "p"

   Examples: Dashboard links
     | link                    | url                                | expected                                         |
     | Change Order            | /dashboard/change-order            | Your current order is                            |
     | Change Collection Point | /dashboard/change-collection-point | Your current collection point is                 |
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


Feature: Leave

  Scenario: _setup:
    Given I switch to the user browser
      And I create a started user "Leaver", "leaver", "leaver@example.com" with password "123123ab"
      And I login with "leaver@example.com" and "123123ab"
    Given I switch to the admin browser
      And I login as a member of staff
      And I navigate to /admin/join/customer/
      And I type "Leaver" into "#searchbar"
      And I click the "Search" button
     Then I see "ACTIVE" in "tr.row1 td.field-account_status"

  Scenario: Haven't left, but navigate to /dashboard/bye
     When I navigate to /dashboard/bye
     Then the browser moves to /dashboard

  Scenario: Leave and change mind
    Given I navigate to /dashboard/leave
      And I see "We're sorry to see you go" in "p"
     When I follow the "< Cancel" link
     Then the browser moves to /dashboard
     # Check I haven't left
    Given I navigate to /dashboard/leave
     Then I see "Leave" in "h1"

  Scenario: Actually Leave
    Given I navigate to /dashboard/leave
     When I click the "Leave" button
     Then the browser moves to /dashboard/bye
      And I see "We'll miss you" in "h1"
    # Check that the admin has the correct status
    Given I switch to the admin browser
     When I navigate to /admin/join/customer/?q=leaver
     Then I see "LEFT" in "tr.row1 td.field-account_status"

  Scenario: Can't leave once left
    Given I switch to the user browser
     When I navigate to /dashboard/leave
     Then I see "You have left the scheme" in "h1"

  Scenario: Once left can only logout, see order history or re-join the scheme
     When I navigate to /dashboard
     Then I see "You have left the scheme" in "h1"
      And there are 3 "input" elements in "#navigation"
      And I see "Dashboard" in "#navigation"
      And I see "Order History" in "#navigation"
      And I see "Log Out" in "#navigation"
      And I see "To re-join the scheme" in "p"

  Scenario Outline: I can still change account details even if I've left the scheme, the navigation just doesn't show
     When I navigate to <url>
     Then I see "Log Out" in "#navigation"

   Examples: Pages I can still visit after I've left
     | url                                |
     | /dashboard                         |
     | /email                             |
     | /password/change                   |
     | /dashboard/change-order            |
     | /dashboard/change-collection-point |
     | /dashboard/bank-details            |
     | /dashboard/order-history           |

  Scenario Outline: Links I can follow after leaving
     Given I navigate to /dashboard
     When I follow the "<link>" link
     Then the browser moves to <url>
      And I see "Dashboard" in "#navigation"
      And I see "Order History" in "#navigation"
      And I see "Log Out" in "#navigation"

   Examples: Links I can follow and their destination
     | link             |  url                               |
     | order            | /dashboard/change-order            |
     | collection point | /dashboard/change-collection-point |
     | bank details     | /dashboard/bank-details            |

  Scenario: Rejoin
    Given I navigate to /dashboard
      And I see "You have left the scheme" in "h1"
     When I click the "Re-Activate" button
     Then the browser is still at /dashboard
      And I see "Successfully re-activated your account" in "#messages"
      And I see "Dashboard" in "h1"
    Given I switch to the admin browser
     When I navigate to /admin/join/customer/?q=leaver
     Then I see "ACTIVE" in "tr.row1 td.field-account_status"

Feature: Leave

  Scenario: _setup:
    Given I create a started user "Leaver", "leaver", "leaver@example.com" with password "123123ab"
     And I login with "leaver@example.com" and "123123ab"

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

  Scenario: Can't leave once left
     When I navigate to /dashboard/leave
     Then I see "You have left the scheme" in "h1"

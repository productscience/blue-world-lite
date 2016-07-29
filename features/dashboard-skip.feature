Feature: Skip Weeks

  Scenario: _setup
    Given I'm using the user browser
      And I create a started user "Skip Weeks", "skip-weeks", "skip-weeks@example.com" with password "123123ab"

  Scenario: Freeze time just before a deadline
    # Using UTC so this is an hour behind
    Given I freeze time at 2016-07-24 13:59:59
      And I login with "skip-weeks@example.com" and "123123ab"
      And I hover over "#navigation .your_order"
      And I follow the "Skip Weeks" link in "#navigation"

  Scenario: Make no changes
     When I click the "Confirm" button
     Then the browser is still at /dashboard/skip-weeks
      And I see "You haven't made any changes to your skip weeks." in "#messages"

  Scenario: Cancel
     When I click the "Cancel" button
     Then the browser moves to /dashboard
      And I see "Your skip weeks have not been changed" in "#messages"

  Scenario: Add a new skip week
    Given I navigate to /dashboard/skip-weeks
      And I see "Mon 25 Jul 2016" in "#id_form-0-display-date"
      And there are 9 "input[type=checkbox]:not(:checked)" elements in "form"
      And I click on "#id_form-0-skipped"
     When I click the "Confirm" button
     Then the browser moves to /dashboard
      And I see "Your skip weeks have been updated successfully" in "#messages"
      # XXX Should we also show skip weeks on the dashboard?
     When I navigate to /dashboard/skip-weeks
     Then "#id_form-0-skipped" is checked
      And I see "Mon 25 Jul 2016" in "#id_form-0-display-date"
      And there are 8 "input[type=checkbox]:not(:checked)" elements in "form"
      And there is 1 "input[type=checkbox]:checked" element in "form"

  Scenario: Unskip an already skipped week
    Given I navigate to /dashboard/skip-weeks
      And I see "Mon 25 Jul 2016" in "#id_form-0-display-date"
      And there are 8 "input[type=checkbox]:not(:checked)" elements in "form"
      And there is 1 "input[type=checkbox]:checked" element in "form"
      And "#id_form-0-skipped" is checked
      And I click on "#id_form-0-skipped"
     When I click the "Confirm" button
     Then the browser moves to /dashboard
      And I see "Your skip weeks have been updated successfully" in "#messages"
     When I navigate to /dashboard/skip-weeks
     Then "#id_form-0-skipped" is not checked
      And I see "Mon 25 Jul 2016" in "#id_form-0-display-date"
      And there are 9 "input[type=checkbox]:not(:checked)" elements in "form"
      And there are 0 "input[type=checkbox]:checked" elements in "form"

  Scenario: Skip the first week again
    Given I navigate to /dashboard/skip-weeks
      And I see "Mon 25 Jul 2016" in "#id_form-0-display-date"
      And I click on "#id_form-0-skipped"
     When I click the "Confirm" button
     Then the browser moves to /dashboard

  Scenario: Move time to just after the deadline
    # Using UTC so this is an hour behind
    Given I freeze time at 2016-07-24 14:00:00
      And I login with "skip-weeks@example.com" and "123123ab"
      And I hover over "#navigation .your_order"
      And I follow the "Skip Weeks" link in "#navigation"

  Scenario: Can no longer see the skipped week
     When I navigate to /dashboard/skip-weeks
     Then there are 8 "input[type=checkbox]:not(:checked)" elements in "form"
      And I see "Mon 01 Aug 2016" in "#id_form-0-display-date"

  Scenario: _teardown
    Given I return to the current time
      And I navigate to /logout

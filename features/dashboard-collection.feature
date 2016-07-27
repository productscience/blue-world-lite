Feature: Dashboard

  Scenario: _setup
    Given I switch to the user browser
      And I create a started user "Dashboard Collection", "dashboard-collection", "dashboard-collection@example.com" with password "123123ab"

  Scenario Outline: Dashboard information
    # Need to freeze time first, otherwise you get logged out because of the session time of 20 mins
    Given I freeze time at <date>
      And I switch to the admin browser
      And I login as a member of staff
      And I navigate to /admin/join/collectionpoint/
      And I follow the "The Old Fire Station" link
      And I choose "<collection_day>" from "#id_collection_day"
      And I click the "Save" button
      And I switch to the user browser
      And I login with "dashboard-collection@example.com" and "123123ab"
     When I navigate to /dashboard
      And I see "and your next collection is" in "#message"
     Then I see "<collection_date>" in "#collection-date"
      And I see "<deadline>" in "#deadline"
      And I see "<changes_affect>" in "#changes-affect"
    Given I freeze time at 2016-07-15 14:00:00
      And I login with "dashboard-collection@example.com" and "123123ab"
      And I navigate to /dashboard/skip-weeks
      And "<week_to_skip>" is not checked
      And I click on "<week_to_skip>"
     When I click the "Confirm" button
     Then the browser moves to /dashboard
    Given I freeze time at <date>
      And I login with "dashboard-collection@example.com" and "123123ab"
      And I navigate to /dashboard
      And I see "but your next collection is skipped so there is nothing for you to pick up" in "#message"
      And I see "<skipped_collection_date>" in "#collection-date"
      And I see "<deadline>" in "#deadline"
      And I see "<changes_affect>" in "#changes-affect"
    Given I freeze time at 2016-07-15 14:00:00
      And I login with "dashboard-collection@example.com" and "123123ab"
    Given I navigate to /dashboard/skip-weeks
      And "<week_to_skip>" is checked
      And I click on "<week_to_skip>"
     When I click the "Confirm" button
     Then the browser moves to /dashboard

   # 17th is a Sunday. IMPORTANT: Notice the behaviour on Thursday depends on the collection point chosen.
   Examples: Times where you can make changes for the next collection
     | date                | day       | collection_day         | week_to_skip       | skipped_collection_date             | collection_date                  | deadline        | changes_affect            |
     | 2016-07-17 14:59:59 | Sunday    | Wednesday              | #id_form-0-skipped | on Wednesday                        | Wednesday                        | 3pm today       | next week's collection    |
     | 2016-07-17 14:59:59 | Sunday    | Thursday               | #id_form-0-skipped | on Thursday                         | Thursday                         | 3pm today       | next week's collection    |
     | 2016-07-17 14:59:59 | Sunday    | Wednesday and Thursday | #id_form-0-skipped | on Wednesday or Thursday            | Wednesday and Thursday           | 3pm today       | next week's collection    |
     | 2016-07-17 15:00:00 | Sunday    | Wednesday              | #id_form-0-skipped | on Wednesday                        | Wednesday                        | 3pm next Sunday | the collection after next |
     | 2016-07-17 15:00:00 | Sunday    | Thursday               | #id_form-0-skipped | on Thursday                         | Thursday                         | 3pm next Sunday | the collection after next |
     | 2016-07-17 15:00:00 | Sunday    | Wednesday and Thursday | #id_form-0-skipped | on Wednesday or Thursday            | Wednesday and Thursday           | 3pm next Sunday | the collection after next |
     | 2016-07-18 00:00:00 | Monday    | Wednesday              | #id_form-0-skipped | on Wednesday                        | Wednesday                        | 3pm this Sunday | next week's collection    |
     | 2016-07-18 00:00:00 | Monday    | Thursday               | #id_form-0-skipped | on Thursday                         | Thursday                         | 3pm this Sunday | next week's collection    |
     | 2016-07-18 00:00:00 | Monday    | Wednesday and Thursday | #id_form-0-skipped | on Wednesday or Thursday            | Wednesday and Thursday           | 3pm this Sunday | next week's collection    |
     | 2016-07-19 00:00:00 | Tuesday   | Wednesday              | #id_form-0-skipped | tomorrow                            | tomorrow                         | 3pm this Sunday | next week's collection    |
     | 2016-07-19 00:00:00 | Tuesday   | Thursday               | #id_form-0-skipped | on Thursday                         | Thursday                         | 3pm this Sunday | next week's collection    |
     | 2016-07-19 00:00:00 | Tuesday   | Wednesday and Thursday | #id_form-0-skipped | tomorrow or Thursday                | tomorrow and Thursday            | 3pm this Sunday | next week's collection    |
     | 2016-07-20 00:00:00 | Wednesday | Wednesday              | #id_form-0-skipped | today                               | today                            | 3pm this Sunday | next week's collection    |
     | 2016-07-20 00:00:00 | Wednesday | Thursday               | #id_form-0-skipped | tomorrow                            | tomorrow                         | 3pm this Sunday | next week's collection    |
     | 2016-07-20 00:00:00 | Wednesday | Wednesday and Thursday | #id_form-0-skipped | today or tomorrow                   | today and tomorrow               | 3pm this Sunday | next week's collection    |
     | 2016-07-21 00:00:00 | Thursday  | Wednesday              | #id_form-1-skipped | on Wednesday next week              | Wednesday next week              | 3pm this Sunday | next week's collection    |
     | 2016-07-21 00:00:00 | Thursday  | Thursday               | #id_form-0-skipped | today                               | today                            | 3pm this Sunday | next week's collection    |
     | 2016-07-21 00:00:00 | Thursday  | Wednesday and Thursday | #id_form-0-skipped | today                               | today                            | 3pm this Sunday | next week's collection    |
     | 2016-07-22 00:00:00 | Friday    | Wednesday              | #id_form-1-skipped | on Wednesday next week              | Wednesday next week              | 3pm this Sunday | next week's collection    |
     | 2016-07-22 00:00:00 | Friday    | Thursday               | #id_form-1-skipped | on Thursday next week               | Thursday next week               | 3pm this Sunday | next week's collection    |
     | 2016-07-22 00:00:00 | Friday    | Wednesday and Thursday | #id_form-1-skipped | on Wednesday or Thursday next week  | Wednesday and Thursday next week | 3pm this Sunday | next week's collection    |
     | 2016-07-23 00:00:00 | Saturday  | Wednesday              | #id_form-1-skipped | on Wednesday next week              | Wednesday next week              | 3pm tomorrow    | next week's collection    |
     | 2016-07-23 00:00:00 | Saturday  | Thursday               | #id_form-1-skipped | on Thursday next week               | Thursday next week               | 3pm tomorrow    | next week's collection    |
     | 2016-07-23 00:00:00 | Saturday  | Wednesday and Thursday | #id_form-1-skipped | on Wednesday or Thursday next week  | Wednesday and Thursday next week | 3pm tomorrow    | next week's collection    |

  Scenario: _teardown
    Given I return to the current time
      And I navigate to /logout

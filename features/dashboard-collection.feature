Feature: Dashboard Collection

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

   # 17th is a Sunday. IMPORTANT: Notice the behaviour on Thursday depends on the collection point chosen.
   # NOTE: All the times are in UTC, so are an hour behind what you'd expect in BST for July
   Examples: Times where you can make changes for the next collection
     | date                | day       | collection_day         | collection_date                  | deadline        | changes_affect            |
     | 2016-07-17 13:59:59 | Sunday    | Wednesday              | Wednesday                        | 3pm today       | next week's collection    |
     | 2016-07-17 13:59:59 | Sunday    | Thursday               | Thursday                         | 3pm today       | next week's collection    |
     | 2016-07-17 13:59:59 | Sunday    | Wednesday and Thursday | Wednesday and Thursday           | 3pm today       | next week's collection    |
     | 2016-07-17 14:00:00 | Sunday    | Wednesday              | Wednesday                        | 3pm next Sunday | the collection after next |
     | 2016-07-17 14:00:00 | Sunday    | Thursday               | Thursday                         | 3pm next Sunday | the collection after next |
     | 2016-07-17 14:00:00 | Sunday    | Wednesday and Thursday | Wednesday and Thursday           | 3pm next Sunday | the collection after next |
     | 2016-07-18 00:00:00 | Monday    | Wednesday              | Wednesday                        | 3pm this Sunday | next week's collection    |
     | 2016-07-18 00:00:00 | Monday    | Thursday               | Thursday                         | 3pm this Sunday | next week's collection    |
     | 2016-07-18 00:00:00 | Monday    | Wednesday and Thursday | Wednesday and Thursday           | 3pm this Sunday | next week's collection    |
     | 2016-07-19 00:00:00 | Tuesday   | Wednesday              | tomorrow                         | 3pm this Sunday | next week's collection    |
     | 2016-07-19 00:00:00 | Tuesday   | Thursday               | Thursday                         | 3pm this Sunday | next week's collection    |
     | 2016-07-19 00:00:00 | Tuesday   | Wednesday and Thursday | tomorrow and Thursday            | 3pm this Sunday | next week's collection    |
     | 2016-07-20 00:00:00 | Wednesday | Wednesday              | today                            | 3pm this Sunday | next week's collection    |
     | 2016-07-20 00:00:00 | Wednesday | Thursday               | tomorrow                         | 3pm this Sunday | next week's collection    |
     | 2016-07-20 00:00:00 | Wednesday | Wednesday and Thursday | today and tomorrow               | 3pm this Sunday | next week's collection    |
     | 2016-07-21 00:00:00 | Thursday  | Wednesday              | Wednesday next week              | 3pm this Sunday | next week's collection    |
     | 2016-07-21 00:00:00 | Thursday  | Thursday               | today                            | 3pm this Sunday | next week's collection    |
     | 2016-07-21 00:00:00 | Thursday  | Wednesday and Thursday | today                            | 3pm this Sunday | next week's collection    |
     | 2016-07-22 00:00:00 | Friday    | Wednesday              | Wednesday next week              | 3pm this Sunday | next week's collection    |
     | 2016-07-22 00:00:00 | Friday    | Thursday               | Thursday next week               | 3pm this Sunday | next week's collection    |
     | 2016-07-22 00:00:00 | Friday    | Wednesday and Thursday | Wednesday and Thursday next week | 3pm this Sunday | next week's collection    |
     | 2016-07-23 00:00:00 | Saturday  | Wednesday              | Wednesday next week              | 3pm tomorrow    | next week's collection    |
     | 2016-07-23 00:00:00 | Saturday  | Thursday               | Thursday next week               | 3pm tomorrow    | next week's collection    |
     | 2016-07-23 00:00:00 | Saturday  | Wednesday and Thursday | Wednesday and Thursday next week | 3pm tomorrow    | next week's collection    |

  Scenario: _teardown
    Given I return to the current time
      And I navigate to /logout

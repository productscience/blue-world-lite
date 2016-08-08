Feature: Become user
  Scenario: _setup
    Given I switch to the user browser
      And I navigate to /logout
      And I navigate to /admin/logout/
      And I create a started user "Reminder", "reminder", "reminder@example.com" with password "123123ab"
      And I login as a member of staff

  Scenario: See reminders
    Given I navigate to /admin/join/customer/?q=Reminder
      And I follow the "Reminder" link in "#result_list .field-full_name"
      Then I see "Reminders" in "#content-main"

  @wip
  Scenario: Set a reminder
    Given I switch to the admin browser
      When I view the customer profile for "Reminder"
      And I create an incomplete reminder for the next week
      Then I should see the reminder on their profile

  @wip
  Scenario: Setting a reminder and filtering
    Given a have a second user with no reminders
    When I navigate to /admin/join/customer/?q=Reminder
      And I follow the "Only with reminders" link in ".changelist-filter"
      Then I should only see "Reminder"

  Scenario: _teardown
    Given I navigate to /admin/logout

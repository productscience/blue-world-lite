Feature: Customer admin
  Scenario: _setup
    Given I switch to the user browser
      And I create a started user "Customer One", "customer-one", "customer-one@example.com" with password "123123ab"
      And I create a started user "Customer Two", "customer-two", "customer-two@example.com" with password "123123ab"
      And I login as a member of staff

  Scenario: Can navigate to Customer
    Given I navigate to /admin
      And I follow the "Customers" link
      And the browser moves to /admin/join/customer/

  Scenario: Can search for customer
    Given I type "One" into "#searchbar"
     When I click the "Search" button
     Then there is 1 "tr" element in ".results tbody"
      And I see "Customer One" in ".field-full_name"
      And I see "ACTIVE" in ".field-account_status"
      And I see "1 x Large veg" in ".field-bag_quantities"
      And I see "The Old Fire Station" in ".field-collection_point"

  Scenario: Customer view
     When I follow the "Customer One" link

     Then I see "User" in ".field-user label"
      And there are 0 "input" elements in ".field-user"
      And I see "Account status" in ".field-account_status label"
      And there are 0 "input" elements in ".field-account_status"
      And I see "Full name" in ".field-full_name label"
      And I see "Nickname" in ".field-nickname label"
      And I see "Mobile" in ".field-mobile label"
      And I see "Gocardless current mandate" in ".field-current_mandate label"
      And there are 0 "input" elements in ".field-current_mandate"
      And I see "Collection point" in ".field-collection_point label"
      And there are 0 "input" elements in ".field-collection_point"
      And I see "Bag quantities" in ".field-bag_quantities label"
      And there are 0 "input" elements in ".field-bag_quantities"
      And I see "Tags" in ".field-tags label"

  Scenario Outline: Edit field errors
    Given I type "<full_name>" into "#id_full_name"
      And I type "<nickname>" into "#id_nickname"
      And I type "<mobile>" into "#id_mobile"
     When I click the "Save" button
     Then I see "Please correct the error below." in "p.errornote"

   Examples: Error data
     | full_name    | nickname     | mobile       |
     |              | customer-one | 01234 567890 |
     | Customer One |              | 01234 567890 |
  

  Scenario: Can save with empty mobile
    Given I navigate to /admin/join/customer/
     When I follow the "Customer One" link
      And I type "Customer One" into "#id_full_name"
      And I type "customer-one" into "#id_nickname"
      And I type "" into "#id_mobile"
     When I click the "Save" button
     Then the browser moves to /admin/join/customer/
      And I see "changed successfully" in ".messagelist .success"

  Scenario: Updated details shown
     When I follow the "Customer One" link
      And I type "Edited Customer One" into "#id_full_name"
      And I type "edited-customer-one" into "#id_nickname"
      And I type "01234 987654" into "#id_mobile"
     When I click the "Save" button
     Then the browser moves to /admin/join/customer/
      And I see "changed successfully" in ".messagelist .success"

    Given I type "One" into "#searchbar"
     When I click the "Search" button
     Then there is 1 "tr" element in ".results tbody"
      And I see "Edited Customer One" in ".field-full_name"
      And I see "ACTIVE" in ".field-account_status"
      And I see "1 x Large veg" in ".field-bag_quantities"
      And I see "The Old Fire Station" in ".field-collection_point"

  Scenario: _teardown
    Given I navigate to /admin/logout/

Feature: Change Order

  Scenario: _setup
    Given I'm using the user browser
      And I create a started user "Change Order", "change-order", "change-order@example.com" with password "123123ab"
      And I login with "change-order@example.com" and "123123ab"
      And there is 1 "li" element in "#order"
      And I see "1 x Large veg" in "#order li:nth-child(1)"
      And I follow the "Change Order" link

  Scenario: Make no changes
     When I click the "Confirm" button
     Then the browser is still at /dashboard/change-order
      And I see "You haven't made any changes to your order." in "#messages"

  Scenario: Cancel
     When I click the "Cancel" button
     Then the browser moves to /dashboard
      And I see "Your order has not been changed" in "#messages"
      And there is 1 "li" element in "#order"
      And I see "1 x Large veg" in "#order li:nth-child(1)"

  Scenario: Can't continue to collection point if I've only chosen one small fruit
    Given I navigate to /dashboard/change-order
      And I type "0" into "#id_form-0-quantity"
      And I type "0" into "#id_form-1-quantity"
      And I type "1" into "#id_form-2-quantity"
     When I click the "Confirm" button
     Then the browser is still at /dashboard/change-order
      And I see "You must choose another bag too if you order small fruit" in ".errorlist"

  Scenario: Change order
    Given I navigate to /dashboard/change-order
     When I type "2" into "#id_form-1-quantity"
      And I click the "Confirm" button
     Then the browser moves to /dashboard
      And I see "Your order has been updated successfully" in "#messages"
      And there are 2 "li" elements in "#order"
      And I see "1 x Large veg" in "#order li:nth-child(1)"
      And I see "2 x Large no pots" in "#order li:nth-child(2)"

Feature: Join in one go

  Scenario: Visit /join to start choosing a bag
    Given I'm using the user browser
     When I navigate to /join
     Then the browser moves to /join/choose-bags/
     When I navigate to /join/
     Then the browser moves to /join/choose-bags/

  Scenario: Can't continue to collection point if you don't have at least one bag
     When I navigate to /join/collection-point/
     Then I see "You have not chosen any bags" in "h3"

  Scenario: Can't continue to sign up if you don't have at least one bag
     When I navigate to /join/signup/
     Then I see "You have not chosen any bags" in "h3"

  Scenario: Must choose at least one bag
    Given I navigate to /join/choose-bags/
      And I see "Which bags do you want to pick up each week?" in "h3"
     When I click the "Choose collection point" button
     Then the browser is still at /join/choose-bags/
      And I see "Please choose at least one bag to order" in "#errors"

  Scenario: Choose bags then go back to edit your previous selection
    Given I navigate to /join/choose-bags/
      And I see "Which bags do you want to pick up each week?" in "h3"
      # One of the inputs from the test data is active=False so is excluded
      And there are 3 "input" elements in "form"
      And the value of "#id_form-1-quantity" is "0"
      And the value of "#id_form-2-quantity" is "0"
      And I type "1" into "#id_form-2-quantity"
      And I click the "Choose collection point" button
      And the browser moves to /join/collection-point/
    Given I navigate to /join/choose-bags/
      And the value of "#id_form-1-quantity" is "0"
      And the value of "#id_form-2-quantity" is "1"
      And there are 3 "input" elements in "form"
      And I type "2" into "#id_form-2-quantity"
     When I click the "Choose collection point" button
     Then the browser moves to /join/collection-point/
    Given I navigate to /join/choose-bags/
      And the value of "#id_form-1-quantity" is "0"
      And the value of "#id_form-2-quantity" is "2"
      And there are 3 "input" elements in "form"
     When I click the "Choose collection point" button
     Then the browser moves to /join/collection-point/

  Scenario: Can't continue to sign up if you don't have at least one collection_point
     When I navigate to /join/signup/
     Then I see "You must choose a collection point" in "h3"

  Scenario: Must choose your collection point
    Given I navigate to /join/collection-point/
      And I see "Where do you want to pick up your bag from?" in "h3"
     When I click the "Next" button
     Then the browser is still at /join/collection-point/
      And I see "This field is required" in "#errors"

  Scenario: Choose bags, and collection points then go back to edit your previous selection
    Given I navigate to /join/collection-point/
      And I see "Where do you want to pick up your bag from?" in "h3"
      # One of the inputs from the test data is active=False so is excluded
      And there are 4 "input" elements in "form"
      And there are 0 "input[selected]" elements in "form"
      # Springfield has no location entered so has no <small> tag
      And I click the "The Old Fire Station" label
     When I click the "Next" button
     Then the browser moves to /join/signup/
      And I see "Sign Up" in "h1"
    Given I navigate to /join/choose-bags/
     Then the value of "#id_form-1-quantity" is "0"
      And the value of "#id_form-2-quantity" is "2"
      And there are 3 "input" elements in "form"
     When I navigate to /join/collection-point/
     Then there are 4 "input" elements in "form"
      And there is 1 "input[selected]" element in "form"
      And the value of "input[name=collection_point]" is "1"

  Scenario Outline: Logo links to home page
    Given I'm using the user browser
      And I navigate to <url>
     When I follow the "Members Home" link
     Then the browser moves to /

   Examples: Pages that should link back to home
     | url                     |
     | /join/choose-bags/      |
     | /join/collection-point/ |
     | /join/signup/           |

  Scenario: Click the sign up button again and bag and collection point choices are lost
    Given I navigate to /
     When I click the "Join the scheme" button
     Then the browser moves to /join/choose-bags/
      And the value of "#id_form-1-quantity" is "0"
      And the value of "#id_form-2-quantity" is "0"
     When I navigate to /join/collection-point/
      And I see "You have not chosen any bags" in "h3"
    Given I navigate to /join/choose-bags/
      And I type "1" into "#id_form-2-quantity"
     When I click the "Choose collection point" button
     Then the browser moves to /join/collection-point/
      And there are 0 "input[selected]" elements in "form"
    Given I click the "The Old Fire Station" label
     When I click the "Next" button
     Then the browser moves to /join/signup/


  # Check that we get the correct errors when things we've selected are deleted or deactivated


  Scenario: Sign up
    Given I clear any sent emails
      And I navigate to /join/signup/
      And I type "a01_join_user@example.com" into "#id_email"
      And I type "123123ab" into "#id_password1"
      And I type "User's Full Name" into "#id_full_name"
      And I type "Nickname" into "#id_nickname"
      And I type "01234 567890" into "#id_mobile"
     When I click the "Sign Up" button
     Then the browser moves to /confirm-email/
      And I see "Verify Your E-mail Address" in "h1"
      And 1 email has been sent
      And I fetch the first sent email
     # Should have stored the data here.
      And the email is to "a01_join_user@example.com"
      And the email is from "no-reply@blueworld.example.com"
      And the email subject is "[BlueWorld] Please Confirm Your E-mail Address"
    Given I'm using the admin browser
      And I login as a superuser
      And I follow the "Email confirmations" link
      And I follow the "a01_join_user@example.com (a01_join_user)" link
      And I capture the value of "#id_key" to the "key" variable
      And the formatted email body contains "http://localhost:8000/confirm-email/{key}/"
    Given I switch to the user browser
     When I navigate to the formatted url /confirm-email/{key}/
     Then I see "Confirm E-mail Address" in "h1"
      And I see "Please confirm that a01_join_user@example.com is an e-mail address for user a01_join_user." in "body"
     When I click the "Confirm" button
     Then the browser moves to /dashboard/
      And I see "Dashboard" in "h1"
      And I see "Successfully signed in as a01_join_user." in "ul"


  Scenario Outline: Can't visit join pages now I've joined an am signed in
    Given I'm using the user browser
      And I navigate to <url>
      And I see "You cannot join if you are already a signed in user" in "h3"
     When I follow the "visit the dashboard" link
     Then the browser moves to /dashboard/

   Examples: Pages that should link back to home
     | url                     |
     | /join/choose-bags/      |
     | /join/collection-point/ |
     | /join/signup/           |

  Scenario Outline: Dashboard Links
    Given I'm using the user browser
     And I navigate to /dashboard/
     When I follow the "<link>" link
     Then the browser moves to <url>
      And I see "This functionality is not implemented yet" in "p"

   Examples: Dashboard links
     | link                    | url                                 |
     | Change order            | /dashboard/change-order/            |
     | Change collection point | /dashboard/change-collection-point/ |


  Scenario: I can logout from the dashboard
    Given I'm using the user browser
      And I navigate to /dashboard/
     When I follow the "Log out" link
     Then the browser moves to /
      # Messages
      And I see "You have signed out." in "ul"

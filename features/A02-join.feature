Feature: Join in one go

  Scenario: Visit /join to start choosing a bag
    Given I'm using the user browser
     When I navigate to /join
     Then the browser moves to /join/choose-bags/
     When I navigate to /join/
     Then the browser moves to /join/choose-bags/

  Scenario: Choose bag (without placing an order for now)
    Given I navigate to /join/choose-bags/
      And I see "Which bags do you want to pick up each week?" in "h1"
     When I click the "Next" button
     Then the browser moves to /join/collection-point/
      And I see "Where do you want to pick up your bag from?" in "h1"

  Scenario: Choose collection point (not real data for now)
    Given I navigate to /join/collection-point/
      And I see "Where do you want to pick up your bag from?" in "h1"
     When I click the "Next" button
     Then the browser moves to /account/signup/
      And I see "Sign Up" in "h1"

  Scenario: Sign up
    Given I clear any sent emails
      And I navigate to /account/signup/
      And I type "a01_join_user@example.com" into "#id_email"
      And I type "123123ab" into "#id_password1"
     When I click the "Sign Up »" button
     Then the browser moves to /account/confirm-email/
      And I see "Verify Your E-mail Address" in "h1"
      And 1 email has been sent
      And I fetch the first sent email
      And the email is to "a01_join_user@example.com"
      And the email is from "no-reply@blueworld.example.com"
      And the email subject is "[BlueWorld] Please Confirm Your E-mail Address"
    Given I'm using the admin browser
      And I login as a superuser
      And I follow the "Email confirmations" link
      And I follow the "a01_join_user@example.com (a01_join_user)" link
      And I capture the value of "#id_key" to the "key" variable
      And the formatted email body contains "http://localhost:8000/account/confirm-email/{key}/"
    Given I switch to the user browser
     When I navigate to the formatted url /account/confirm-email/{key}/
     Then I see "Confirm E-mail Address" in "h1"
      And I see "Please confirm that a01_join_user@example.com is an e-mail address for user a01_join_user." in "body"
     When I click the "Confirm" button
     Then the browser moves to /dashboard/
      And I see "Dashboard" in "h1"
      And I see "Successfully signed in as a01_join_user." in "ul"




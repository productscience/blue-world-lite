Feature: Sign up

   Scenario: Navigate to sign up
     Given I'm using the user browser
       And I navigate to /accounts/signup/
       And I see "Sign Up" in "h1"
       And I see "Already have an account? Then please sign in" in "body"
      When I navigate to /accounts/signup
      Then I see "Sign Up" in "h1"
       And I see "Already have an account? Then please sign in" in "body"

   Scenario: Can navigate to log in page
     Given I navigate to /accounts/signup/
      When I follow the "sign in" link
      Then the browser moves to /accounts/login/
       And I see "Sign In" in "h1"

   Scenario: Get an error if the password is too short
      Given I navigate to /accounts/signup/
       And I type "james@example.com" into "#id_email"
       And I type "1" into "#id_password1"
      When I click the "Sign Up »" button
       And I see "Password must be a minimum of 6 characters." in ".errorlist li"

   Scenario: Sign up
     Given I clear any sent emails
       And I navigate to /accounts/signup/
       And I type "james@example.com" into "#id_email"
       And I type "123123ab" into "#id_password1"
      When I click the "Sign Up »" button
      Then the browser moves to /accounts/confirm-email/
       And I see "Verify Your E-mail Address" in "h1"
       And I see "Confirmation e-mail sent to james@example.com." in "li"
       And I see "We have sent an e-mail to you for verification." in "body"
       And I see "Follow the link provided to finalize the signup process." in "body"
       And I see "Please contact us if you do not receive it within a few minutes." in "body"
       And 1 email has been sent
       And I fetch the first sent email
       And the email is to "james@example.com"
       And the email is from "no-reply@blueworld.example.com"
       And the email subject is "[example.com] Please Confirm Your E-mail Address"
       And the email body contains "http://localhost:8000/accounts/confirm-email/"

   Scenario: Get an error if the email is being used by another registered user
      Given I navigate to /accounts/signup/
       And I type "james@example.com" into "#id_email"
       And I type "123123ab" into "#id_password1"
      When I click the "Sign Up »" button
      Then the browser is still at /accounts/signup/
       And I see "A user is already registered with this e-mail address." in ".errorlist li"

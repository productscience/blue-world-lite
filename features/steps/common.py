from browserstep.common import *
from browserstep.sentmail import *


@step('I login as a superuser')
def step_impl(context):
    context.execute_steps(
        '''
        Given I navigate to /admin/logout/
          And I navigate to /admin/login/
          And I see "Django administration" in "h1"
          And I see "Username" in "body"
          And I see "Password" in "body"
          And I type "superuser" into "#id_username"
          And I type "123123ab" into "#id_password"
         When I click the "Log in" button
         Then the browser moves to /admin/
          And I see "superuser" in "#user-tools"
        '''
    )


@step('I create user "{fullname}", "{nickname}", "{email}" with password "{password}"')
def step_impl(context, fullname, nickname, email, password):
    context.execute_steps(
        '''
        Given I create user "{fullname}", "{nickname}", "{email}" with password "{password}" and login
        And I navigate to /logout
        '''.format(
            fullname=fullname,
            nickname=nickname,
            email=email,
            password=password,
        )
    )


@step('I create user "{fullname}", "{nickname}", "{email}" with password "{password}" and login')
def step_impl(context, fullname, nickname, email, password):
    context.execute_steps(
        '''
        Given I switch to the user browser
          And I navigate to /join/choose-bags/
          And I type "1" into "#id_form-1-quantity"
          And I click the "Choose collection point" button
          And the browser moves to /join/collection-point/
          And I click the "The Old Fire Station" label
         When I click the "Next" button
         Then the browser moves to /join/signup/

        Given I clear any sent emails
          And I type "{email}" into "#id_email"
          And I type "{password}" into "#id_password1"
          And I type "{fullname}" into "#id_full_name"
          And I type "{nickname}" into "#id_nickname"
          # Mobile is optiona;
          And I type "01234 567890" into "#id_mobile"
         When I click the "Sign Up" button
         Then the browser moves to /confirm-email/
          And I see "Verify Your E-mail Address" in "h1"
          And 1 email has been sent
          And I fetch the first sent email
          And the email is to "{email}"

        Given I'm using the admin browser
          And I login as a superuser
          And I follow the "Email confirmations" link
          And I follow the "{email} ({email_username})" link
          And I capture the value of "#id_key" to the "key" variable
          And the formatted email body contains "http://localhost:8000/confirm-email/{{key}}/"

        Given I switch to the user browser
         When I navigate to the formatted url /confirm-email/{{key}}/
         Then I see "Confirm E-mail Address" in "h1"
         When I click the "Confirm" button
         Then the browser moves to /dashboard/
          And I see "Dashboard" in "h1"
        '''.format(
            fullname=fullname,
            nickname=nickname,
            email=email,
            password=password,
            email_username=email.split('@')[0],
        )
    )

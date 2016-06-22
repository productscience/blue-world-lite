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



@step('I choose one large veg box to collect from the Old Fire Station')
def step_impl(context):
    context.execute_steps(
        '''
         Given I navigate to /join/choose-bags
          And I type "1" into "#id_form-1-quantity"
          And I click the "Next" button
          And the browser moves to /join/collection-point
          And I click the "The Old Fire Station" label
         When I click the "Next" button
         Then the browser moves to /join/login-details
        '''
    )


@step('I create user "{fullname}", "{nickname}", "{email}" with password "{password}"')
def step_impl(context, fullname, nickname, email, password):
    context.execute_steps(
        '''
        Given I switch to the user browser
          And I navigate to /logout
          And I choose one large veg box to collect from the Old Fire Station

        Given I clear any sent emails
          And I type "{email}" into "#id_email"
          And I type "{password}" into "#id_password1"
          And I type "{fullname}" into "#id_full_name"
          And I type "{nickname}" into "#id_nickname"
         When I click the "Sign Up" button
         Then the browser moves to /confirm-email
          And I fetch the first sent email

        Given I'm using the admin browser
          And I login as a superuser
          And I follow the "Email confirmations" link
          And I follow the "{email} ({email_username})" link
          And I capture the value of "#id_key" to the "key" variable

        Given I switch to the user browser
          And I navigate to the formatted url /confirm-email/{{key}}/
          And I click the "Confirm" button
         Then the browser moves to /dashboard
          And I see "Dashboard" in "h1"
          And I navigate to /logout
        '''.format(
            fullname=fullname,
            nickname=nickname,
            email=email,
            password=password,
            email_username=email.split('@')[0],
        )
    )


@step('I login with "{login}" and "{password}"')
def step_impl(context, login, password):
    context.execute_steps(
        '''
    Given I switch to the user browser
      And I navigate to /logout
      And I navigate to /login
      And I see "Log In" in "h1"
      And I type "{login}" into "#id_login"
      And I type "{password}" into "#id_password"
     When I click the "Log in" button
     Then the browser moves to /dashboard
        '''.format(login=login, password=password)
    )

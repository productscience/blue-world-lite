import time
from datetime import timedelta


from browserstep.common import *
from browserstep.debug import *
from browserstep.popup import *
from browserstep.sentmail import *

from selenium.webdriver.common.action_chains import ActionChains

from django.utils import timezone


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


@step('I login as a member of staff')
def step_impl(context):
    context.execute_steps(
        '''
        Given I navigate to /admin/logout/
          And I navigate to /admin/login/
          And I see "Django administration" in "h1"
          And I see "Username" in "body"
          And I see "Password" in "body"
          And I type "staff" into "#id_username"
          And I type "123123ab" into "#id_password"
         When I click the "Log in" button
         Then the browser moves to /admin/
          And I see "staff" in "#user-tools"
        '''
    )


@step('I choose one large veg box to collect from the Old Fire Station')
def step_impl(context):
    context.execute_steps(
        '''
         Given I navigate to /join/choose-bags
          And I type "1" into "#id_form-0-quantity"
          And I click the "Next" button
          And the browser moves to /join/collection-point
          And I click the "The Old Fire Station" label
         When I click the "Next" button
         Then the browser moves to /join/login-details
        '''
    )


CREATE_USER_STEPS = '''
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
          And I capture the value of "/confirm-email/(.*)/" in the message to the "key" variable
         When I navigate to the formatted url /confirm-email/{{key}}/
          And I click on ".confirm button"
'''


# # Users have these states:
# * email verified
# * Go Cardless
# * Started
# * Membership Status

@step('I create an email verified user "{fullname}", "{nickname}", "{email}" with password "{password}"')
def step_impl(context, fullname, nickname, email, password):
    context.execute_steps(
        (
            CREATE_USER_STEPS + '''
            And I navigate to /logout
            '''
        ).format(
            fullname=fullname,
            nickname=nickname,
            email=email,
            password=password,
            email_username=email.split('@')[0],
        )
    )


@step('I create a started user "{fullname}", "{nickname}", "{email}" with password "{password}"')
def step_impl(context, fullname, nickname, email, password):
    context.execute_steps(
        (
             CREATE_USER_STEPS + '''
             Then the browser moves to /dashboard/gocardless
              And I see "Set up Go Cardless" in "h1"
              And I click the "Set up Go Cardless" button
              And I see "Dashboard" in "h1"
              And I navigate to /logout
            '''
        )
        .format(
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

@step('I login with "{login}" and "{password}" without GoCardless')
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
     Then the browser moves to /dashboard/gocardless
        '''.format(login=login, password=password)
    )

@step('I view the customer profile for "{customer}"')
def step_impl(context, customer):


    ''''
    # context.execute_steps(
    #     '''
    # Given I switch to the admin browser
    #     And I navigate to /admin/join/customer/?q={customer}
    #     And I follow the "{customer}" link in "#result_list .field-full_name"
    #     '''.format(customer=customer)
    # )


@step('I have created an incomplete reminder for the next week')
def step_impl(context):

    next_week = timezone.now() + timedelta(weeks=1)
    context.browser.find_elements_by_link_text('Add another Reminder')[0].click()

    context.execute_steps(
        '''
        Given I follow the "Add another Reminder" link
        And I type "Reminder Title" into "#id_reminder_set-0-title"
        And I type {} into "#id_reminder_set-0-date"
        And I type "Important Reminder text" into "#id_reminder_set-0-details"
        And I click the "Save" button
        ''').format(next_week.strftime('%Y-%m-%d'))


import requests

@step('I time travel to {date}')
def step_impl(context, date):
    r = requests.get('http://localhost:8000/timetravel/to/'+date)
    assert r.status_code == 200, r.status_code
    assert r.text == 'ok'

@step('I freeze time at {date}')
def step_impl(context, date):
    r = requests.get('http://localhost:8000/timetravel/freeze/'+date)
    assert r.status_code == 200, r.status_code
    assert r.text == 'ok'

@step('I return to the current time')
def step_impl(context):
    r = requests.get('http://localhost:8000/timetravel/cancel')
    assert r.status_code == 200, r.status_code
    assert r.text == 'ok'

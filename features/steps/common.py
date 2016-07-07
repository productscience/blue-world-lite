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

        Given I'm using the admin browser
          And I login as a superuser
          And I follow the "Email confirmations" link
          And I follow the "{email} ({email_username})" link
          And I capture the value of "#id_key" to the "key" variable

        Given I switch to the user browser
          And I navigate to the formatted url /confirm-email/{{key}}/
          And I click the "Confirm" button
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
             Then the browser moves to /dashboard
              And I see "Set up Go Cardless" in "h1"
              And I follow the "Skip" link
              And the browser is still at /dashboard
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


@step('I debug')
def step_impl(context):
    import pdb; pdb.set_trace()

@then(u'"{selector}" is checked')
def step_impl(context, selector):
    element = context.browser.find_element_by_css_selector(selector)
    assert element is not None, "No such element found"
    assert element.get_attribute('checked') == 'true', "Element is not checked"

@then(u'the alert says "{text}"')
def step_impl(context, text):
    if context.browser_vendor == 'phantomjs':
        raise Exception("PhantomJS does not support alerts")
    alert = context.browser.switch_to_alert()
    assert alert.text == text

@then(u'I cancel the alert')
def step_impl(context):
    if context.browser_vendor == 'phantomjs':
        raise Exception("PhantomJS does not support alerts")
    alert = context.browser.switch_to_alert()
    alert.dismiss()

@then(u'I accept the alert')
def step_impl(context):
    if context.browser_vendor == 'phantomjs':
        raise Exception("PhantomJS does not support alerts")
    alert = context.browser.switch_to_alert()
    alert.accept()


import re
@step('I capture the value of "{regex}" in the message to the "{name}" variable')
def step_impl(context, regex, name):
    if not hasattr(context, 'variables'):
        context.variables = {}
    reg = re.compile(regex)
    string = context.message['message_raw']
    value = reg.search(string).group(1)
    context.variables[name] = value
    print(context.variables)

@step('I type "" into "{selector}"')
def step_impl(context, selector):
    element = context.browser.find_element_by_css_selector(selector)
    assert element is not None, "No such element found"
    element.clear()


from freezegun import freeze_time
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

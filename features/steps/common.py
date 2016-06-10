from browserstep.common import *
from browserstep.sentmail import *


@step('I login as a superuser')
def step_impl(context):
    context.execute_steps('''
    Given I navigate to /admin
      And the browser moves to /admin/login/?next=/admin/
      And I see "Django administration" in "h1"
      And I see "Username" in "body"
      And I see "Password" in "body"
      And I type "superuser" into "#id_username"
      And I type "123123ab" into "#id_password"
     When I click the "Log in" button
     Then the browser moves to /admin/
      And I see "superuser" in "#user-tools"
    ''')

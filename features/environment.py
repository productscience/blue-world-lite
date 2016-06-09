import os

from selenium import webdriver


def before_all(context):
    assert 'TEST_DIR' not in os.environ, 'Expected the TEST_DIR envrionment variable not be set'
    assert 'TEST_PROJECT_NAME' not in os.environ, 'Expected the TEST_PROJECT_NAME envrionment variable not be set'
    # if os.path.exists(context.config.userdata['cwd']):
    #     raise Exception('Test directory already exists')
    # os.mkdir(context.config.userdata['cwd'])
    if context.config.userdata.get('driver', 'phantomjs').lower() == 'chrome':
        context.browser = webdriver.Chrome()
    else:
        context.browser = webdriver.PhantomJS()
        context.browser.set_window_size(1120, 550)
    # os.environ['TEST_DIR'] = context.config.userdata['cwd']
    # os.environ['TEST_PROJECT_NAME'] = 'myproject'
    context.failed = False


def after_step(context, step):
    if step.status == "failed" and os.environ.get('TEST_DEBUG', 'false').lower() == 'true':
        import pdb; pdb.set_trace()


def after_all(context):
    context.browser.quit()
    # del os.environ['TEST_DIR']
    # del os.environ['TEST_PROJECT_NAME']


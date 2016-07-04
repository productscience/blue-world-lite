import os

from selenium import webdriver


def before_all(context):
    assert 'TEST_DIR' not in os.environ, 'Expected the TEST_DIR envrionment variable not be set'
    assert 'TEST_PROJECT_NAME' not in os.environ, 'Expected the TEST_PROJECT_NAME envrionment variable not be set'
    # if os.path.exists(context.config.userdata['cwd']):
    #     raise Exception('Test directory already exists')
    # os.mkdir(context.config.userdata['cwd'])
    browser_vendor = context.config.userdata.get('default_browser', 'phantomjs').lower()
    if os.environ.get('BROWSER'):
        browser_vendor = os.environ['BROWSER'].lower()
    assert browser_vendor in ['chrome', 'phantomjs'], 'Only Chrome and PhantomJS are tested for now, not {}'.format(browser_vendor)
    if browser_vendor == 'chrome':
        context.admin_browser = webdriver.Chrome()
        context.user_browser = webdriver.Chrome()
    else:
        context.admin_browser = webdriver.PhantomJS()
        context.admin_browser.set_window_size(1120, 550)
        context.user_browser = webdriver.PhantomJS()
        context.user_browser.set_window_size(1120, 550)
    # os.environ['TEST_DIR'] = context.config.userdata['cwd']
    # os.environ['TEST_PROJECT_NAME'] = 'myproject'
    context.browser = context.user_browser
    context.failed = False


def after_step(context, step):
    if step.status == "failed" and os.environ.get('TEST_DEBUG', 'false').lower() == 'true':
        import pdb; pdb.set_trace()


def after_all(context):
    context.browser.quit()
    # del os.environ['TEST_DIR']
    # del os.environ['TEST_PROJECT_NAME']


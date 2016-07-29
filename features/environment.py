import os

from selenium import webdriver


def before_all(context):
    assert 'TEST_DIR' not in os.environ, 'Expected the TEST_DIR envrionment variable not be set'
    assert 'TEST_PROJECT_NAME' not in os.environ, 'Expected the TEST_PROJECT_NAME envrionment variable not be set'
    browser_vendor = context.config.userdata.get('default_browser', 'phantomjs').lower()
    if os.environ.get('BROWSER'):
        browser_vendor = os.environ['BROWSER'].lower()
    assert browser_vendor in ['chrome', 'phantomjs'], 'Only Chrome and PhantomJS are tested for now, not {}'.format(browser_vendor)
    context.browser_vendor = browser_vendor
    if browser_vendor == 'chrome':
        context.admin_browser = webdriver.Chrome()
        context.user_browser = webdriver.Chrome()
    else:
        context.admin_browser = webdriver.PhantomJS()
        context.admin_browser.set_window_size(1120, 550)
        context.user_browser = webdriver.PhantomJS()
        context.user_browser.set_window_size(1120, 550)
    context.browser = context.user_browser
    # context.admin_browser.implicitly_wait(2)
    # context.user_browser.implicitly_wait(2)
    context.failed = False


def after_step(context, step):
    if step.status == "failed" and os.environ.get('TEST_DEBUG', 'false').lower() == 'true':
        import pdb; pdb.set_trace()


def after_all(context):
    context.browser.quit()

from django.conf.urls import url

from .views import (churn_report, mailchimp_report, db_report, payments_report)

urlpatterns = [
    url(
        r'^churn.csv$', churn_report, name='churn',
    ),
    url(
        r'^mailchimp.csv$', mailchimp_report, name='mailchimp',
    ),
    url(
        r'^db.csv$', db_report, name='db',
    ),
    url(
        r'^payments.csv$', payments_report, name='payments',
    ),
]

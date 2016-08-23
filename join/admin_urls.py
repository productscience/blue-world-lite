from django.conf.urls import url, include
from django.conf import settings
from django.contrib import admin

import join.views as views

urlpatterns = [
    url(
        r'^churn.csv$',
        views.churn_report,
        name='churn',
    ),
    url(
        r'^mailchimp.csv$',
        views.mailchimp_report,
        name='mailchimp',
    ),
    url(
        r'^db.csv$',
        views.db_report,
        name='db',
    ),
    url(
        r'^payments.csv$',
        views.payments_report,
        name='payments',
    ),
]

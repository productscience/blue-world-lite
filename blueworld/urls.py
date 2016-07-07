"""blueworld URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
import join.views
import allauth.account.views as account_views


urlpatterns = [
    url(r'^$', join.views.home, name='home'),
    url(r'^timetravel/to/(?P<date>.+)$', join.views.timetravel_to, name='timetravel_to'),
    url(r'^timetravel/freeze/(?P<date>.+)$', join.views.timetravel_freeze, name='timetravel_freeze'),
    url(r'^timetravel/cancel$', join.views.timetravel_cancel, name='timetravel_cancel'),
    url(r'^join$', join.views.join, name='join'),
    url(r'^join/$', join.views.join),
    url(r'^join/choose-bags$', join.views.choose_bags, name='join_choose_bags'),
    url(r'^join/collection-point$', join.views.collection_point, name='join_collection_point'),
    url(r'^join/login-details$', join.views.signup, name='account_signup'),
    url(r"^confirm-email$", account_views.email_verification_sent, name="account_email_verification_sent"),
    url(r"^login$", account_views.login, name="account_login"),
    url(r"^logout$", account_views.logout, name="account_logout"),
    url(r"^logged-out$", join.views.logged_out, name="account_logged_out"),
    url(r'^admin/', admin.site.urls),
    url(r'^hijack/', include('hijack.urls')),
    url(r'^go-cardless-callback$', join.views.go_cardless_callback, name='go_cardless_callback'),
    url(r'^dashboard$', join.views.dashboard, name='dashboard'),
    url(r'^dashboard/bank-details$', join.views.bank_details, name='dashboard_bank_details'),
    url(r'^dashboard/order-history$', join.views.dashboard_order_history, name='dashboard_order_history'),
    url(r'^dashboard/rejoin-scheme$', join.views.dashboard_rejoin_scheme, name='dashboard_rejoin_scheme'),
    url(r'^dashboard/change-order$', join.views.dashboard_change_order, name='dashboard_change_order'),
    url(r'^dashboard/change-collection-point$', join.views.dashboard_change_collection_point, name='dashboard_change_collection_point'),
    url(r'^dashboard/leave$', join.views.dashboard_leave, name='dashboard_leave'),
    url(r'^dashboard/bye$', join.views.dashboard_bye, name='dashboard_bye'),

    #url(r'^account/', include('allauth.urls')),
    url(r"^password/change/$", account_views.password_change, name="account_change_password"),
    url(r"^password/set/$", account_views.password_set, name="account_set_password"),
    url(r"^inactive/$", account_views.account_inactive, name="account_inactive"),
    url(r"^email/$", account_views.email, name="account_email"),
    url(r"^confirm-email/(?P<key>\w+)/$", account_views.confirm_email, name="account_confirm_email"),

    # password reset
    url(r"^password/reset/$", account_views.password_reset, name="account_reset_password"),
    url(r"^password/reset/done/$", account_views.password_reset_done, name="account_reset_password_done"),
    url(r"^password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$", account_views.password_reset_from_key, name="account_reset_password_from_key"),
    url(r"^password/reset/key/done/$", account_views.password_reset_from_key_done, name="account_reset_password_from_key_done"),
]

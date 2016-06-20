from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden


def home(request):
    if request.method == 'GET':
        return render(request, 'home.html')
    elif request.method == 'POST':
        if request.POST.get('join-scheme', False):
            return redirect(reverse("join_choose_bags"))
        elif request.POST.get('login', False):
            return redirect(reverse("account_login"))
    return HttpResponseBadRequest()


def join(request):
    return redirect(reverse("join_choose_bags"))


def choose_bags(request):
    if request.method == 'GET':
        return render(request, 'choose_bags.html')
    elif request.method == 'POST':
        return redirect(reverse("join_collection_point"))
    return HttpResponseBadRequest()


def collection_point(request):
    if request.method == 'GET':
        return render(request, 'collection_point.html')
    elif request.method == 'POST':
        return redirect(reverse("account_signup"))
    return HttpResponseBadRequest()


def dashboard(request):
    if request.user.username:
        return render(request, 'dashboard.html')
    else:
        return HttpResponseForbidden('<html><body><h1>Not logged in</h1></body></html>')

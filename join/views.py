from django.shortcuts import render
from django.http import HttpResponse


def home(request):
    return HttpResponse('''
      <h1>Home</h1>

      <a href="/accounts/login">Login</a>
      <a href="/accounts/signup">Register</a>
      <a href="/admin/">Staff Login</a>
    ''')

def dashboard(request):
    if request.user.username:
        return HttpResponse('''
          <h1>Dashboard</h1>

          <a href="/accounts/logout">Log out</a>
        ''')
    else:
        return HttpResponse('''Not logged in''')


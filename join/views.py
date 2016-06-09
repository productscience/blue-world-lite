from django.shortcuts import render
from django.http import HttpResponse


def home(request):
    # XXX Needs to consume all the error messages successfully.
    return HttpResponse('''
      <h1>Home</h1>

      <a href="/accounts/login">Login</a>
      <a href="/accounts/signup">Register</a>
      <a href="/admin/">Staff Login</a>
    ''')

def dashboard(request):
    # XXX Needs to consume all the error messages successfully.
    if request.user.username:
        return HttpResponse('''
          <h1>Dashboard</h1>

          <ul>
          <li>If no verified email - needs to ask you to confirm.</li>
          <li>If no no GoCardless - needs to ask you to set that up.</li>
          <li>Otherwise, show the main dashboard</li>
          </ul>
          <a href="/accounts/logout">Log out</a>
        ''')
    else:
        return HttpResponse('''Not logged in''')


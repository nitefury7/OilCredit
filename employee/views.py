from django.shortcuts import render
from django.http import HttpResponse
from home.utils import ensure_auth
from employee.models import EmployeeProfile

@ensure_auth(EmployeeProfile)
def dashboard(request):
    return HttpResponse('Employee dashboard')

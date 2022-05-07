from django.shortcuts import render
from django.http import HttpResponse
from home.utils import ensure_auth
from member.models import MemberProfile

# Create your views here.

@ensure_auth(MemberProfile)
def orders(request):
    return render(request, 'member/orders.html')

@ensure_auth(MemberProfile)
def history(request):
    return render(request, 'member/history.html')

@ensure_auth(MemberProfile)
def profile_settings(request):
    return render(request, 'member/profile_settings.html')
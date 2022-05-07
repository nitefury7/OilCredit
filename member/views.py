from django.shortcuts import render, redirect
from home.utils import ensure_auth
from django.contrib.auth.forms import PasswordChangeForm
from member.forms import MemberProfileForm
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
    form = MemberProfileForm(request.user)
    change_password = PasswordChangeForm(request.user)
    if request.method == 'POST':
        if 'change_password' in request.POST:
            change_password = PasswordChangeForm(request.user, request.POST)
            if change_password.is_valid():
                change_password.save()
                return redirect('member:profile_settings')
        else:
            form = MemberProfileForm(request.user, request.POST)
            if form.is_valid():
                form.save()
                return redirect('member:profile_settings')

    return render(request, 'member/profile_settings.html', {'form': form, 'change_password': change_password})
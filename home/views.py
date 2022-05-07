from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from member.models import MemberProfile
from employee.models import EmployeeProfile
from home.forms import *
from home.utils import redirect_if_auth


@redirect_if_auth
def home(request):
    return render(request, 'home/home.html')


@redirect_if_auth
def login(request):
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                auth_login(request, user)
                if MemberProfile.objects.filter(user=user).exists():
                    return redirect('member:orders')
                if EmployeeProfile.objects.filter(user=user).exists():
                    return redirect('employee:dashboard')
                return redirect("home:home")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'home/login.html', {'form': form})

def logout(request):
    auth_logout(request)
    return redirect('home:home')

@redirect_if_auth
def signup(request):
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user, _ = form.save()
            auth_login(request, user)
            return redirect('member:orders')

    return render(request, 'home/signup.html', {'form': form})

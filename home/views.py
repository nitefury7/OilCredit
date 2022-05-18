from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.views.generic import TemplateView, FormView
from django.utils.decorators import method_decorator
from django.shortcuts import redirect

from home.forms import *
from home.utils import redirect_if_auth


@method_decorator(redirect_if_auth, name='dispatch')
class Home(TemplateView):
    template_name = 'home/home.html'


@method_decorator(redirect_if_auth, name='dispatch')
class Login(FormView):
    template_name = 'home/login.html'
    form_class = AuthenticationForm

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)
        if user:
            auth_login(self.request, user)
        else:
            messages.error(self.request, "Invalid username or password.")
        return redirect("home:home")


def logout(request):
    auth_logout(request)
    return redirect('home:home')


@method_decorator(redirect_if_auth, name='dispatch')
class SignUp(FormView):
    template_name = 'home/signup.html'
    form_class = SignUpForm

    def form_valid(self, form):
        user, _ = form.save()
        auth_login(self.request, user)
        return redirect('customer:orders')

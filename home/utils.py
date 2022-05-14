from member.models import MemberProfile
from employee.models import EmployeeProfile
from django.shortcuts import redirect
from django.http import Http404


def redirect_if_auth(fn):
    def inner(request, *args, **kwargs):
        if request.user.is_authenticated:
            if MemberProfile.objects.filter(user=request.user).exists():
                return redirect('member:orders')
            elif EmployeeProfile.objects.filter(user=request.user).exists():
                return redirect('employee:dashboard')
            elif request.user.is_superuser:
                return redirect('admin:index')
        return fn(request, *args, **kwargs)
    return inner


def get_profile(model, user):
    if model.objects.filter(user=user).exists():
        return model.objects.get(user=user)
    else:
        return None


def ensure_auth(model):
    def decorator(fn):
        def inner(request, *args, **kwargs):
            if request.user.is_authenticated:
                if model.objects.filter(user=request.user).exists():
                    return fn(request, *args, **kwargs)
            raise Http404()
        return inner
    return decorator

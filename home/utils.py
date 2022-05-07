from member.models import MemberProfile
from employee.models import EmployeeProfile
from django.shortcuts import redirect
from django.http import Http404

def redirect_if_auth(fn):
    def inner(request):
        if request.user.is_authenticated:
            if MemberProfile.objects.filter(user=request.user).exists():
                return redirect('member:dashboard')
            elif EmployeeProfile.objects.filter(user=request.user).exists():
                return redirect('employee:dashboard')
        return fn(request)
    return inner


def ensure_auth(model):
    def decorator(fn):
        def inner(request):
            if request.user.is_authenticated:
                if model.objects.filter(user=request.user).exists():
                    return fn(request)
            raise Http404()
        return inner
    return decorator
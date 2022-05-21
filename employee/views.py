from employee.forms import PurchaseFormSet
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.views.generic import ListView, FormView
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect

from home.utils import ensure_auth, get_profile
from customer.models import Invoice
from employee.models import EmployeeProfile
from employee.forms import EmployeeProfileForm


@method_decorator(ensure_auth(EmployeeProfile), name='dispatch')
class Dashboard(ListView):
    model = Invoice
    template_name = 'employee/dashboard.html'
    context_object_name = 'invoices'

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        employee = get_profile(EmployeeProfile, self.request.user)
        return (
            queryset
            .filter(employee=employee)
            .order_by('-order_timestamp')
        )


def place_order(request):
    formset = PurchaseFormSet()
    return render(request, 'employee/place_order.html', {'formset': formset})


@ensure_auth(EmployeeProfile)
def profile_settings(request):
    if request.method == 'POST':
        if 'change_password' in request.POST:
            change_password = PasswordChangeForm(request.user, request.POST)
            if change_password.is_valid():
                change_password.save()
                messages.success(request, 'Password changed successfully.')
                return redirect('home:login')
        else:
            profile_form = EmployeeProfileForm(request.user, request.POST)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Updated profile settings.')
                return redirect('employee:profile_settings')

    profile_form = EmployeeProfileForm(request.user)
    change_password = PasswordChangeForm(request.user)
    return render(
        request,
        'employee/profile_settings.html',
        {'profile_form': profile_form, 'change_password_form': change_password}
    )

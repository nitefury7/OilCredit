from datetime import datetime

from django.db import transaction
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.views.generic import ListView, FormView
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect

from home.utils import ensure_auth, get_profile
from member.models import Invoice
from employee.models import EmployeeProfile
from employee.forms import EmployeeProfileForm, EmployeeOrderForm, SetCredit


@method_decorator(ensure_auth(EmployeeProfile), name='dispatch')
class Dashboard(ListView):
    model = Invoice
    template_name = 'employee/dashboard.html'
    context_object_name = 'invoices'

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        return (
            queryset
            .filter(status=Invoice.Status.PENDING)
            .order_by('-order_timestamp')
        )


@ensure_auth(EmployeeProfile)
def approve_invoice(request, id):
    if Invoice.objects.filter(pk=id).exists():
        invoice = Invoice.objects.get(pk=id)
        invoice.employee = get_profile(EmployeeProfile, request.user)
        invoice.action_timestamp = datetime.now()
        invoice.status = Invoice.Status.APPROVED
        invoice.save()
        messages.success(request, 'The invoice has been approved.')
    else:
        messages.error(request, 'The invoice does not exist.')
    return redirect('employee:dashboard')


@ensure_auth(EmployeeProfile)
def reject_invoice(request, id):
    if Invoice.objects.filter(pk=id).exists():
        invoice = Invoice.objects.get(pk=id)
        if invoice.status == Invoice.Status.PENDING:
            invoice.member.credit += invoice.item.rate * invoice.quantity
            invoice.employee = get_profile(EmployeeProfile, request.user)
            invoice.action_timestamp = datetime.now()
            invoice.status = Invoice.Status.REJECTED
            with transaction.atomic():
                invoice.member.save()
                invoice.save()
            messages.success(request, 'The invoice has been rejected.')
    else:
        messages.error(request, 'Invalid invoice')
    return redirect('employee:dashboard')


@method_decorator(ensure_auth(EmployeeProfile), name='dispatch')
class PlaceOrder(FormView):
    template_name = 'employee/place_order.html'
    form_class = EmployeeOrderForm

    def get_form_kwargs(self):
        employee = get_profile(EmployeeProfile, self.request.user)
        kwargs = super().get_form_kwargs()
        kwargs['employee'] = employee
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request,
            "The order has been placed successfully."
        )
        return redirect('employee:place_order')

@method_decorator(ensure_auth(EmployeeProfile), name='dispatch')
class SetCredit(FormView):
    template_name = 'employee/set_credit.html'
    form_class = SetCredit

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Successfully changed credit of user.')
        return redirect('employee:set_credit')


@ensure_auth(EmployeeProfile)
def profile_settings(request):
    form = EmployeeProfileForm(request.user)
    change_password = PasswordChangeForm(request.user)
    if request.method == 'POST':
        if 'change_password' in request.POST:
            change_password = PasswordChangeForm(request.user, request.POST)
            if change_password.is_valid():
                change_password.save()
                messages.success(request, 'Password changed successfully.')
                return redirect('home:login')
        else:
            form = EmployeeProfileForm(request.user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Updated profile settings.')
                return redirect('employee:profile_settings')

    return render(
        request,
        'employee/profile_settings.html',
        {'form': form, 'change_password': change_password}
    )

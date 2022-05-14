from django.shortcuts import render, redirect
from django.contrib.auth.forms import PasswordChangeForm
from django.db import transaction
from django.contrib import messages
from home.utils import ensure_auth, get_profile
from employee.models import EmployeeProfile
from employee.forms import EmployeeProfileForm, EmployeeOrderForm, SetCredit
from member.models import Invoice
from datetime import datetime


@ensure_auth(EmployeeProfile)
def dashboard(request):
    invoices = Invoice.objects.filter(
        status=Invoice.Status.PENDING).order_by('-order_timestamp')
    return render(request, 'employee/dashboard.html', {'invoices': invoices})


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


@ensure_auth(EmployeeProfile)
def place_order(request):
    profile = get_profile(EmployeeProfile, request.user)
    form = EmployeeOrderForm(profile)
    if request.method == 'POST':
        form = EmployeeOrderForm(profile, request.POST)
        if form.is_valid():
            form.save()
            messages.success( request, "Your order has been placed successfully.")
            return redirect('employee:place_order')
    return render(request, 'employee/place_order.html', {'form': form})


@ensure_auth(EmployeeProfile)
def set_credit(request):
    form = SetCredit()
    if request.method == 'POST':
        form = SetCredit(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully changed credit of user.')
            return redirect('employee:set_credit')

    return render(request, 'employee/set_credit.html', {'form': form})


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

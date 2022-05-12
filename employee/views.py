from django.shortcuts import render, redirect
from django.contrib.auth.forms import PasswordChangeForm
from django.db import transaction
from django.contrib import messages
from home.utils import ensure_auth, get_profile
from employee.models import EmployeeProfile
from employee.forms import EmployeeProfileForm, OrderForm, SetCredit
from member.models import Invoice, MemberProfile
from datetime import datetime


@ensure_auth(EmployeeProfile)
def dashboard(request):
    invoices = Invoice.objects.filter(approved_by=None).order_by('-date')
    return render(request, 'employee/dashboard.html', {'invoices': invoices})


@ensure_auth(EmployeeProfile)
def approve_invoice(request, id):
    if Invoice.objects.filter(pk=id).exists():
        invoice = Invoice.objects.get(pk=id)
        invoice.approved_by = get_profile(EmployeeProfile, request.user)
        invoice.approval_timestamp = datetime.now()
        invoice.save()
    return redirect('employee:dashboard')


@ensure_auth(EmployeeProfile)
def cancel_invoice(_, id):
    if Invoice.objects.filter(pk=id).exists():
        invoice = Invoice.objects.get(pk=id)
        if not invoice.approved():
            invoice.member.credit += invoice.item.rate * invoice.quantity
            with transaction.atomic():
                invoice.member.save()
                invoice.delete()
    return redirect('employee:dashboard')


@ensure_auth(EmployeeProfile)
def place_order(request):
    form = OrderForm()
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            member = form.cleaned_data['member']
            cost = form.cleaned_data['item'].rate * \
                form.cleaned_data['quantity']
            if (member.credit < cost):
                messages.error(
                    request, f"{member.user.username} does not have sufficient credits for this purchase.")
                return redirect('employee:place_order')
            member.credit -= cost

            invoice = form.save(commit=False)
            invoice.member = member
            invoice.date = datetime.now()
            invoice.approved_by = get_profile(EmployeeProfile, request.user)
            invoice.approval_timestamp = datetime.now()

            with transaction.atomic():
                member.save()
                invoice.save()
            messages.success(
                request, "Your order has been placed successfully.")
            return redirect('employee:place_order')
        else:
            messages.error(request, "Sorry, your order couldn't be processed.")
            return redirect('employee:place_order')
    return render(request, 'employee/place_order.html', {'form': form})

# TODO: complete this


@ensure_auth(EmployeeProfile)
def set_credit(request):
    form = SetCredit()
    if request.method == 'POST':
        form = SetCredit(request.POST)
        member = get_profile(MemberProfile, form.cleaned_data.user)
        if member:
            form = SetCredit(request.POST, instance=member)
            if form.is_valid():
                return redirect('employee:dashboard')

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
                return redirect('home:login')
        else:
            form = EmployeeProfileForm(request.user, request.POST)
            if form.is_valid():
                form.save()
                return redirect('employee:profile_settings')
    return render(request, 'employee/profile_settings.html', {'form': form, 'change_password': change_password})

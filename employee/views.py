from django.shortcuts import render, redirect
from django.contrib.auth.forms import PasswordChangeForm
from home.utils import ensure_auth
from employee.models import EmployeeProfile
from employee.forms import EmployeeProfileForm, OrderForm, AddCredit
from member.models import Invoice
from datetime import datetime

@ensure_auth(EmployeeProfile)
def dashboard(request):
    invoices = Invoice.objects.filter(approved=False).order_by('-date')
    return render(request, 'employee/dashboard.html', {'invoices': invoices})

@ensure_auth(EmployeeProfile)
def approve_invoice(request, id):
    if Invoice.objects.filter(pk=id).exists():
        invoice = Invoice.objects.get(pk=id)
        invoice.approved = True
        invoice.save()
    return redirect('employee:dashboard')

@ensure_auth(EmployeeProfile)
def place_order(request):
    form = OrderForm()
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.date = datetime.now()
            invoice.approved = True
            invoice.save()
            return redirect('employee:dashboard')
    return render(request, 'employee/place_order.html', {'form' : form})

@ensure_auth(EmployeeProfile)
def add_credit(request):
    form = AddCredit()
    if request.method == 'POST':
        form = AddCredit(request.POST)
        if form.is_valid():
            
            return redirect('employee:dashboard')

    return render(request, 'employee/add_credit.html', {'form' : form})


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

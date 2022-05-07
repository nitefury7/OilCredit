from django.shortcuts import render, redirect
from home.utils import ensure_auth
from django.contrib.auth.forms import PasswordChangeForm
from member.forms import MemberProfileForm, OrderForm
from member.models import MemberProfile, Invoice
from datetime import datetime

# Create your views here.
@ensure_auth(MemberProfile)
def orders(request):
    form = OrderForm()
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.member = MemberProfile.objects.get(user=request.user)
            invoice.date = datetime.now()
            invoice.save()
            return redirect('member:history')
    return render(request, 'member/orders.html', {'form' : form})

@ensure_auth(MemberProfile)
def history(request):
    invoices = Invoice.objects.filter(member=MemberProfile.objects.get(user=request.user)).order_by('-date')
    return render(request, 'member/history.html', {'invoices' : invoices})

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
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from member.forms import MemberProfileForm, OrderForm
from member.models import MemberProfile, Invoice
from home.utils import ensure_auth, get_profile
from datetime import datetime
from django.db import transaction


@ensure_auth(MemberProfile)
def orders(request):
    member = get_profile(MemberProfile, request.user)

    form = OrderForm()
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            cost = form.cleaned_data['item'].rate * \
                form.cleaned_data['quantity']
            if (member.credit < cost):
                messages.error(
                    request,
                    "You do not have sufficient credits for this purchase."
                )
                return redirect('member:orders')
            member.credit -= cost

            invoice = form.save(commit=False)
            invoice.member = member
            invoice.order_timestamp = datetime.now()

            with transaction.atomic():
                member.save()
                invoice.save()
            messages.success(
                request, "Your order has been placed successfully.")
            return redirect('member:orders')
        else:
            messages.error(request, "Sorry, your order couldn't be processed.")
            return redirect('member:orders')

    invoices = Invoice.objects.filter(member=member).order_by('-order_timestamp')
    return render(
        request,
        'member/orders.html',
        {'member': member, 'form': form, 'invoices': invoices}
    )


@ensure_auth(MemberProfile)
def cancel_order(request, id):
    member = get_profile(MemberProfile, request.user)
    if Invoice.objects.filter(pk=id).exists():
        invoice = Invoice.objects.get(pk=id)
        if invoice.status == Invoice.Status.PENDING and member == invoice.member:
            invoice.member.credit += invoice.item.rate * invoice.quantity
            with transaction.atomic():
                invoice.member.save()
                invoice.delete()
            messages.success(request, 'Your order has been cancelled.')
    else:
        messages.error('Invalid order')

    return redirect('member:orders')


@ensure_auth(MemberProfile)
def profile_settings(request):
    form = MemberProfileForm(request.user)
    change_password = PasswordChangeForm(request.user)
    if request.method == 'POST':
        if 'change_password' in request.POST:
            change_password = PasswordChangeForm(request.user, request.POST)
            if change_password.is_valid():
                change_password.save()
                messages.success(request, 'Password changed successfully')
                return redirect('home:login')
        else:
            form = MemberProfileForm(request.user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Updated profile information')
                return redirect('member:profile_settings')

    member = get_profile(MemberProfile, request.user)
    return render(
        request,
        'member/profile_settings.html',
        {'member': member, 'form': form, 'change_password': change_password}
    )

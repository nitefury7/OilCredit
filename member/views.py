from datetime import datetime

from django.db import transaction
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.views.generic import FormView
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect

from member.forms import MemberProfileForm, OrderForm
from member.models import MemberProfile, Invoice
from home.utils import ensure_auth, get_profile


@method_decorator(ensure_auth(MemberProfile), name='dispatch')
class Orders(FormView):
    template_name = 'member/orders.html'
    form_class = OrderForm

    def get_form_kwargs(self):
        member = get_profile(MemberProfile, self.request.user)
        kwargs = super().get_form_kwargs()
        kwargs['member'] = member
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Your order has been placed successfully.")
        return redirect('member:orders')

    def get_context_data(self, **kwargs):
        member = get_profile(MemberProfile, self.request.user)
        context = super().get_context_data(**kwargs)
        context['member'] = member
        context['invoices'] = Invoice.objects.filter(
            member=context['member']).order_by('-order_timestamp')
        return context

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

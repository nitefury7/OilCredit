import json

from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.views.generic import ListView
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect

from customer.forms import CustomerProfileForm
from customer.models import Item, CustomerProfile, Invoice
from home.utils import ensure_auth, get_profile


@method_decorator(ensure_auth(CustomerProfile), name='dispatch')
class Orders(ListView):
    model = Invoice
    context_object_name = 'invoices'
    template_name = 'customer/orders.html'

    def get_queryset(self):
        qs = super().get_queryset()
        customer = get_profile(CustomerProfile, self.request.user)
        return qs.filter(customer=customer).order_by('-order_timestamp')


@ensure_auth(CustomerProfile)
def spendings_by_product(request):
    customer = get_profile(CustomerProfile, request.user)
    items = Item.objects.all()
    sales_dict = {}
    for item in items:
        invoices = Invoice.objects.filter(item=item, customer=customer)
        sales = sum(invoice.cost() for invoice in invoices)
        sales_dict[str(item)] = sales
    return HttpResponse(json.dumps(sales_dict), content_type='application/json')


@ensure_auth(CustomerProfile)
def profile_settings(request):
    form = CustomerProfileForm(request.user)
    change_password = PasswordChangeForm(request.user)
    if request.method == 'POST':
        if 'change_password' in request.POST:
            change_password = PasswordChangeForm(request.user, request.POST)
            if change_password.is_valid():
                change_password.save()
                messages.success(request, 'Password changed successfully')
                return redirect('home:login')
        else:
            form = CustomerProfileForm(request.user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Updated profile information')
                return redirect('customer:profile_settings')

    customer = get_profile(CustomerProfile, request.user)
    return render(
        request,
        'customer/profile_settings.html',
        {'customer': customer, 'form': form, 'change_password': change_password}
    )

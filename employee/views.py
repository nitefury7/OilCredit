import json
import csv
from collections import OrderedDict
from datetime import datetime
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.views.generic import ListView
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.shortcuts import render, redirect

from home.utils import ensure_auth, get_profile
from customer.models import CustomerProfile, Invoice, Item, Purchase
from employee.models import EmployeeProfile
from employee.forms import EmployeeProfileForm, PurchaseForm


@method_decorator(ensure_auth(EmployeeProfile), name='dispatch')
class InvoiceHistory(ListView):
    model = Invoice
    template_name = 'employee/invoice_history.html'
    context_object_name = 'invoices'

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        employee = get_profile(EmployeeProfile, self.request.user)
        return (
            queryset
            .filter(employee=employee)
            .order_by('-order_timestamp')
        )


@ensure_auth(EmployeeProfile)
def get_customers(_):
    customers = []
    for customer in CustomerProfile.objects.all():
        customers.append({
            "id": customer.pk,
            "username": customer.user.username,
        })
    return JsonResponse(customers, safe=False)


@ensure_auth(EmployeeProfile)
def get_customer_profile(request, id):
    customer = get_object_or_404(CustomerProfile, pk=id)

    contact = ""
    if customer.contact:
        e164 = customer.contact.as_e164
        contact = f"{e164[:-10]} {e164[-10:]}"

    return JsonResponse({
        "id": customer.id,
        "username": customer.user.username,
        "first_name": customer.user.first_name,
        "last_name": customer.user.last_name,
        "email": customer.user.email,
        "contact": contact,
        "credit": customer.credit,
    })


@ensure_auth(EmployeeProfile)
def get_items(_):
    items = []
    for item in Item.objects.all():
        items.append({
            "id": item.pk,
            "name": item.name,
        })
    return JsonResponse(items, safe=False)


@ensure_auth(EmployeeProfile)
def set_credit(request):
    if request.method == 'POST':
        json_form = json.loads(request.body)
        customer = get_object_or_404(CustomerProfile, pk=json_form['customer'])
        customer.credit = json_form["credit"]
        try:
            customer.save()
            messages.success(request, "Set credit successfully.")
        except:
            messages.error(request, "Cannot set credit.")
    return HttpResponse(status=400)


@ensure_auth(EmployeeProfile)
def place_order(request):
    if request.method == 'POST':
        json_form = json.loads(request.body)
        if Invoice.objects.filter(pk=json_form["invoice_id"]).exists():
            messages.error(request, "This invoice ID already exists!")
            return HttpResponse(status=400)

        customer = get_object_or_404(CustomerProfile, pk=json_form['customer'])
        invoice = Invoice(pk=json_form["invoice_id"],
                          customer=customer,
                          order_timestamp=timezone.now(),
                          employee=get_profile(EmployeeProfile, request.user))

        forms = [PurchaseForm(purchase) for purchase in json_form['purchases']]

        if not forms:
            messages.error(request, "Cannot process empty form")
            return HttpResponse(status=400)
        elif all([form.is_valid() for form in forms]):
            purchases = [form.save(commit=False) for form in forms]

            if customer.credit < sum(purchase.total for purchase in purchases):
                messages.error(request, "Not enough credit")
                return HttpResponse(status=400)

            with transaction.atomic():
                invoice.save()
                for purchase in purchases:
                    purchase.invoice = invoice
                    purchase.save()
                customer.credit -= invoice.cost()
                customer.save()

            messages.success(request, "Your order was placed.")
            return HttpResponse("")
        else:
            msgs = []
            for form in forms:
                errors = [f"{field}: {','.join(error_list)}" for field,
                          error_list in form.errors.items()]
                msgs.extend(errors)
            msgs = "".join([f"<li>{msg}</li>" for msg in msgs])
            messages.error(request, f"<ul>{msgs}</ul>")
            return HttpResponse(status=400)

    return render(request, 'employee/place_order.html')


def export_invoices(qs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Invoices_{}.csv"'.format(datetime.now())
        writer = csv.writer(response, dialect='excel')

        header = ['Date', 'ACC. No.', 'Name', 'INV. No.']
        items = OrderedDict()
        for item in Item.objects.all():
            items[item.pk] = item.name

        for item in [(f"Volume {item_name}", f"Price {item_name}")
                     for item_name in items.values()]:
            header.extend(item)
        header.append('Total')
        writer.writerow(header)

        for invoice in qs:
            details = []
            details.extend([
                invoice.order_timestamp,
                invoice.customer.pk,
                invoice.customer.user.username,
                invoice.id,
            ])
            purchases = Purchase.objects.filter(invoice=invoice.pk)
            purchases_dict = {}
            for purchase in purchases:
                purchases_dict[purchase.item.pk] = (
                    purchase.volume, purchase.total)
            for item_id in items:
                details.extend(purchases_dict.get(item_id, (0, 0)))
            details.append(invoice.cost())
            writer.writerow(details)

        return response

@ensure_auth(EmployeeProfile)
def export_all_invoices(_):
    return export_invoices(Invoice.objects.all())

@ensure_auth(EmployeeProfile)
def export_daily_invoices(_):
    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    return export_invoices(Invoice.objects.filter(order_timestamp__gte=today))

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

import json

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
from customer.models import CustomerProfile, Invoice, Item
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
    })


@ensure_auth(EmployeeProfile)
def get_items(_):
    items = []
    for item in Item.objects.all():
        items.append({
            "id": item.pk,
            "rate": item.rate,
            "name": item.name,
            "can_set_price": item.can_set_price
        })
    return JsonResponse(items, safe=False)


@ensure_auth(EmployeeProfile)
def place_order(request):
    if request.method == 'POST':
        json_form = json.loads(request.body)
        profile = get_object_or_404(CustomerProfile, pk=json_form['customer'])
        invoice = Invoice(customer=profile,
                          order_timestamp=timezone.now(),
                          employee=get_profile(EmployeeProfile, request.user))

        forms = [PurchaseForm(purchase) for purchase in json_form['purchases']]

        if not forms:
            messages.error(request, "Cannot process empty form")
            return HttpResponse(status=400)
        elif all([form.is_valid() for form in forms]):
            objects = [form.save(commit=False) for form in forms]
            with transaction.atomic():
                invoice.save()
                for object in objects:
                    object.invoice = invoice
                    object.save()
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

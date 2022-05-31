import json
import csv
from collections import OrderedDict
from datetime import datetime, timedelta

from django.urls import path
from django.http import HttpResponse
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from employee.models import EmployeeProfile
from customer.models import CustomerProfile, Invoice, Item, Purchase


class EmployeeProfileInline(admin.StackedInline):
    model = EmployeeProfile
    extra = 0


class CustomerProfileInline(admin.StackedInline):
    model = CustomerProfile
    extra = 0


class UserAdmin(BaseUserAdmin):
    inlines = (EmployeeProfileInline, CustomerProfileInline)
    list_display = ("username", "user_type", "first_name",
                    "last_name", "email")
    list_filter = ("is_superuser", "is_active")

    def user_type(self, user):
        if user.is_superuser:
            return 'Admin'
        elif CustomerProfile.objects.filter(user=user).exists():
            return 'Customer'
        elif EmployeeProfile.objects.filter(user=user).exists():
            return 'Employee'
        return 'None'


class CustomAdminSite(admin.AdminSite):
    site_title = 'Dashboard'
    site_header = '𝄜 Admin Dashboard'
    index_title = 'Oil Company Index'

    def index(self, request, extra_context=None):
        if not extra_context:
            extra_context = {}

        extra_context = {
            'customer_count': CustomerProfile.objects.count,
            'employee_count': EmployeeProfile.objects.count,
            'total_sales': sum(invoice.cost() for invoice in Invoice.objects.all()),
            'items': Item.objects.count,
        }
        return super().index(request, extra_context)

    def get_urls(self):
        urls = super().get_urls()
        return [
            path('sales_by_item', self.admin_view(
                self.sales_by_item), name='sales_by_item'),
            path('recent_sales', self.admin_view(
                self.recent_sales), name='recent_sales'),
            path('recent_customers', self.admin_view(
                self.recent_customers), name='recent_customers'),
            path('export_all_invoices', self.admin_view(
                self.export_all_invoices), name='export_all_invoices'),
            path('export_daily_invoices', self.admin_view(
                self.export_daily_invoices), name='export_daily_invoices'),
        ] + urls

    def recent_customers(self, _):
        today = datetime.today()
        new_customers = []
        prev_date = datetime.now()
        for i in range(10):
            date = today - timedelta(days=i)
            customers = CustomerProfile.objects.filter(
                user__date_joined__gte=date,
                user__date_joined__lte=prev_date
            )
            new_customers.append(len(customers))
            prev_date = date

        return HttpResponse(
            json.dumps(list(reversed(new_customers))),
            content_type='application/json'
        )

    def recent_sales(self, _):
        today = datetime.today()
        invoices_all = Invoice.objects.all()
        sales = []
        prev_date = datetime.now()
        for i in range(10):
            date = today - timedelta(days=i)
            invoices = invoices_all.filter(
                order_timestamp__gte=date,
                order_timestamp__lte=prev_date
            )
            sales.append(sum(invoice.cost() for invoice in invoices))
            prev_date = date

        return HttpResponse(json.dumps(list(reversed(sales))), content_type='application/json')

    def sales_by_item(self, _):
        items = Item.objects.all()
        sales_dict = {}
        for item in items:
            purchases = Purchase.objects.filter(item=item)
            sales = sum(purchase.cost() for purchase in purchases)
            sales_dict[str(item)] = sales
        return HttpResponse(json.dumps(sales_dict), content_type='application/json')

    def export_all_customers(self, _):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=All_Members.csv'
        writer = csv.writer(response)
        ...
        return response

    def export_all_invoices(self, _):
        return self.export_invoices(Invoice.objects.all())

    def export_daily_invoices(self, _):
        last_date = datetime.now() - timedelta(days=1)
        return self.export_invoices(Invoice.objects.filter(order_timestamp__gte=last_date))

    def export_invoices(self, qs):

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=All_Invoices.csv'
        writer = csv.writer(response)

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
                    purchase.volume, purchase.rate)
            for item_id in items:
                details.extend(purchases_dict.get(item_id, (0, 0)))
            details.append(invoice.cost())
            writer.writerow(details)

        return response


admin_site = CustomAdminSite()
admin_site.register(User, UserAdmin)

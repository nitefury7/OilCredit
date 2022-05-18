import json
from datetime import datetime, timedelta

from django.urls import path
from django.http import HttpResponse
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from employee.models import EmployeeProfile
from customer.models import CustomerProfile, Invoice, Item


class EmployeeProfileInline(admin.StackedInline):
    model = EmployeeProfile
    extra = 0


class CustomerProfileInline(admin.StackedInline):
    model = CustomerProfile
    extra = 0


class UserAdmin(BaseUserAdmin):
    inlines = (EmployeeProfileInline, CustomerProfileInline)
    list_display = ("username", "email", "first_name",
                    "last_name", "user_type")
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
            invoices = Invoice.objects.filter(item=item)
            sales = sum(invoice.cost() for invoice in invoices)
            sales_dict[str(item)] = sales
        return HttpResponse(json.dumps(sales_dict), content_type='application/json')


admin_site = CustomAdminSite()
admin_site.register(User, UserAdmin)

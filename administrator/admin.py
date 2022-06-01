import csv
from collections import OrderedDict
from datetime import timedelta

from django.urls import path
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
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
            path('export_all_customers', self.admin_view(
                self.export_all_customers), name='export_all_customers'),
            path('export_all_employees', self.admin_view(
                self.export_all_employees), name='export_all_employees'),
            path('export_employee_report', self.admin_view(
                self.export_employee_report), name='export_employee_report'),
        ] + urls

    def recent_customers(self, _):
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        new_customers = []
        for i in range(10):
            date = today - timedelta(days=i)
            customers = CustomerProfile.objects.filter(
                user__date_joined__gte=date,
                user__date_joined__lte=date + timedelta(days=1)
            )
            new_customers.append(len(customers))

        return JsonResponse(list(reversed(new_customers)), safe=False)

    def recent_sales(self, _):
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        invoices_all = Invoice.objects.all()
        sales = []
        for i in range(10):
            date = today - timedelta(days=i)
            invoices = invoices_all.filter(
                order_timestamp__gte=date,
                order_timestamp__lte=date + timedelta(days=1)
            )
            sales.append(sum(invoice.cost() for invoice in invoices))

        return JsonResponse(list(reversed(sales)), safe=False)

    def sales_by_item(self, _):
        items = Item.objects.all()
        sales_dict = {}
        for item in items:
            purchases = Purchase.objects.filter(item=item)
            sales = sum(purchase.cost() for purchase in purchases)
            sales_dict[str(item)] = sales
        return JsonResponse(sales_dict)

    def export_invoices(self, qs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=All_Invoices.csv'
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
                    purchase.volume, purchase.cost())
            for item_id in items:
                details.extend(purchases_dict.get(item_id, (0, 0)))
            details.append(invoice.cost())
            writer.writerow(details)

        return response

    def export_all_invoices(self, _):
        return self.export_invoices(Invoice.objects.all())

    def export_daily_invoices(self, _):
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return self.export_invoices(Invoice.objects.filter(order_timestamp__gte=today))

    def export_all_customers(self, _):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=All_Customers.csv'
        writer = csv.writer(response, dialect='excel')
        header = ('Customer ID', 'Username', 'First Name', 'Last Name', 'Email',
                  'Contact', 'Gender', 'City', 'State', 'Zip Code', )
        writer.writerow(header)
        for customer in CustomerProfile.objects.all():
            contact = ""
            if customer.contact:
                e164 = customer.contact.as_e164
                contact = f"{e164[:-10]} {e164[-10:]}"

            row = (
                customer.id, customer.user.username, customer.user.first_name, customer.user.last_name,
                customer.user.email, contact, customer.get_gender_display(), customer.city,
                customer.state, customer.zip_code,
            )
            writer.writerow(row)
        return response

    def export_all_employees(self, _):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=All_Employees.csv'
        writer = csv.writer(response, dialect='excel')
        header = ('Employee ID', 'Username', 'First Name', 'Last Name', 'Email', 'Contact', 'Gender',
                  'City', 'State', 'Zip Code', 'Employee Type', "Employment Date", "Post")
        writer.writerow(header)
        for employee in EmployeeProfile.objects.all():
            contact = ""
            if employee.contact:
                e164 = employee.contact.as_e164
                contact = f"{e164[:-10]} {e164[-10:]}"
            row = (
                employee.id, employee.user.username, employee.user.first_name, employee.user.last_name,
                employee.user.email, contact, employee.get_gender_display(), employee.city,
                employee.state, employee.zip_code, employee.employee_type, employee.employment_date, employee.post
            )
            writer.writerow(row)
        return response

    def export_employee_report(self, _):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=Daily_Employee_Report.csv'
        writer = csv.writer(response, dialect='excel')
        header = ['Employee ID', 'Username', 'First Name', 'Last Name',
                  'Total Sales', 'Total Volume Sold', 'Total Customers Served', ]

        items = OrderedDict()
        for item in Item.objects.all():
            items[item.pk] = item.name
        for item_name in items.values():
            header.extend([f"Volume of {item_name} sold",
                           f"Sales of {item_name}", ])
        writer.writerow(header)

        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        for employee in EmployeeProfile.objects.all():
            invoices = Invoice.objects.filter(
                employee=employee, order_timestamp__gte=today)
            total_sales = sum(x.cost() for x in invoices)
            total_customers_served = len(invoices)

            purchases = Purchase.objects.filter(
                invoice__employee=employee, invoice__order_timestamp__gte=today)
            total_volume_sold = sum(x.volume for x in purchases)

            details = [
                employee.id, employee.user.username, employee.user.first_name, employee.user.last_name,
                total_sales, total_volume_sold, total_customers_served
            ]

            purchases_dict = {item_id: (0, 0) for item_id in items}
            for purchase in purchases:
                v, c = purchases_dict[purchase.item.pk]
                purchases_dict[purchase.item.pk] = (
                    v + purchase.volume, c + purchase.cost())

            for item_id in items:
                details.extend(purchases_dict[item_id])
            writer.writerow(details)
        return response


admin_site = CustomAdminSite()
admin_site.register(User, UserAdmin)

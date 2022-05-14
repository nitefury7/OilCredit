import json
from datetime import datetime, timedelta

from django.urls import path
from django.http import HttpResponse
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from employee.models import EmployeeProfile
from member.models import MemberProfile, Invoice, Item


class EmployeeProfileInline(admin.StackedInline):
    model = EmployeeProfile
    extra = 0


class MemberProfileInline(admin.StackedInline):
    model = MemberProfile
    extra = 0


class UserAdmin(BaseUserAdmin):
    inlines = (EmployeeProfileInline, MemberProfileInline)
    list_display = ("username", "email", "first_name",
                    "last_name", "user_type")
    list_filter = ("is_superuser", "is_active")

    def user_type(self, user):
        if user.is_superuser:
            return 'Admin'
        elif MemberProfile.objects.filter(user=user).exists():
            return 'Member'
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
            'member_count': MemberProfile.objects.count,
            'employee_count': EmployeeProfile.objects.count,
            'total_sales': sum(invoice.cost() for invoice in Invoice.objects.filter(status=Invoice.Status.APPROVED)),
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
            path('recent_members', self.admin_view(
                self.recent_members), name='recent_members'),
        ] + urls

    def recent_members(self, _):
        today = datetime.today()
        new_members = []
        prev_date = datetime.now()
        for i in range(10):
            date = today - timedelta(days=i)
            members = MemberProfile.objects.filter(
                user__date_joined__gte=date,
                user__date_joined__lte=prev_date
            )
            new_members.append(len(members))
            prev_date = date

        return HttpResponse(
            json.dumps(list(reversed(new_members))),
            content_type='application/json'
        )

    def recent_sales(self, _):
        today = datetime.today()
        approved_invoices = Invoice.objects.filter(
            status=Invoice.Status.APPROVED)
        sales = []
        prev_date = datetime.now()
        for i in range(10):
            date = today - timedelta(days=i)
            invoices = approved_invoices.filter(
                action_timestamp__gte=date,
                action_timestamp__lte=prev_date
            )
            sales.append(sum(invoice.cost() for invoice in invoices))
            prev_date = date

        return HttpResponse(json.dumps(list(reversed(sales))), content_type='application/json')

    def sales_by_item(self, _):
        items = Item.objects.all()
        sales_dict = {}
        for item in items:
            invoices = Invoice.objects.filter(
                item=item, status=Invoice.Status.APPROVED)
            sales = sum(invoice.cost() for invoice in invoices)
            sales_dict[str(item)] = sales
        return HttpResponse(json.dumps(sales_dict), content_type='application/json')


admin_site = CustomAdminSite()
admin_site.register(User, UserAdmin)

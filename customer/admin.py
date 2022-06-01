from django.contrib import admin
from customer.models import *
from administrator.admin import admin_site

# Register your models here.
admin_site.register(Item)


class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'customer', 'order_timestamp', 'employee',)


admin_site.register(Invoice, InvoiceAdmin)

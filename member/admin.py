from django.contrib import admin
from member.models import *
from administrator.admin import admin_site

# Register your models here.
admin_site.register(Item)
admin_site.register(MemberType)


class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'member', 'order_timestamp', 'employee',)


admin_site.register(Invoice, InvoiceAdmin)

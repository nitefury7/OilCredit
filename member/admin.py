from django.contrib import admin
from member.models import *

# Register your models here.

admin.site.register(Item)
admin.site.register(MemberType)

class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'member', 'date', 'approved_by',)

admin.site.register(Invoice, InvoiceAdmin)

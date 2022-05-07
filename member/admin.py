from django.contrib import admin

# Register your models here.
from member.models import *

admin.site.register(MemberProfile)
admin.site.register(Item)
admin.site.register(MemberType)
admin.site.register(Invoice)
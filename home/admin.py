from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from employee.models import EmployeeProfile
from member.models import MemberProfile


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


admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.site_title = 'Dashboard'
admin.site.site_header = '𝄜 Admin Dashboard'
admin.site.index_title = 'Oil Company Index'

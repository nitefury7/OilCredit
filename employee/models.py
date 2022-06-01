from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from home.models import Gender


class EmployeeType(models.IntegerChoices):
    TEMPORARY, PERMANENT = range(2)


class EmployeeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.SmallIntegerField(choices=Gender.choices)
    city = models.CharField(max_length=20, blank=True)
    state = models.CharField(max_length=20, blank=True)
    zip_code = models.BigIntegerField(blank=True, null=True)
    contact = PhoneNumberField(blank=True)
    employee_type = models.SmallIntegerField(choices=EmployeeType.choices)
    employment_date = models.DateField()
    post = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.user.username}"

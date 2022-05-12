from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import MinValueValidator

from employee.models import EmployeeProfile


class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=2000)
    rate = models.FloatField()

    def __str__(self):
        return f"{self.name}"


class MemberType(models.Model):
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=1000)
    value = models.FloatField()

    def __str__(self):
        return f"{self.name}"


class MemberProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    member_type = models.ForeignKey(
        MemberType, on_delete=models.CASCADE, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=(
        ('M', 'Male'), ('F', 'Female'), ('O', 'Other')))
    city = models.CharField(max_length=20, blank=True)
    state = models.CharField(max_length=20, blank=True)
    zip_code = models.BigIntegerField(blank=True, null=True)
    contact = PhoneNumberField(blank=True)
    credit = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}"


class Invoice(models.Model):
    member = models.ForeignKey(MemberProfile, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    date = models.DateTimeField()
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    approved_by = models.ForeignKey(
        EmployeeProfile, on_delete=models.CASCADE, blank=True, null=True)
    approval_timestamp = models.DateTimeField(blank=True, null=True)

    def approved(self):
        return self.approved_by is not None

    def __str__(self):
        return f"{self.member.user.username} {'ordered' if self.approved() else 'requested'} {self.quantity} {self.item.name} "

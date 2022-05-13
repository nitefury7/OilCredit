from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import MinValueValidator

from home.models import Gender
from employee.models import EmployeeProfile


class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=2000)
    rate = models.FloatField()

    def __str__(self):
        return str(self.name)


class MemberType(models.Model):
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=1000)
    value = models.FloatField()

    def __str__(self):
        return str(self.name)


class MemberProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    member_type = models.ForeignKey(
        MemberType,
        on_delete=models.CASCADE, blank=True, null=True,
    )

    gender = models.SmallIntegerField(choices=Gender.choices)

    city = models.CharField(max_length=20, blank=True)
    state = models.CharField(max_length=20, blank=True)
    zip_code = models.BigIntegerField(blank=True, null=True)
    contact = PhoneNumberField(blank=True)
    credit = models.FloatField(default=0, validators=(MinValueValidator(0),))

    def __str__(self):
        return str(self.user.username)


class Invoice(models.Model):
    member = models.ForeignKey(MemberProfile, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    order_timestamp = models.DateTimeField()
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    employee = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.CASCADE, blank=True, null=True,
    )
    action_timestamp = models.DateTimeField(blank=True, null=True)

    class Status(models.IntegerChoices):
        PENDING, APPROVED, REJECTED = range(3)

    status = models.SmallIntegerField(
        choices=Status.choices,
        default=Status.PENDING
    )

    def approved(self):
        return self.status == Invoice.Status.APPROVED

    def __str__(self):
        return f"{self.member.user.username} - {self.quantity} {self.item.name}"

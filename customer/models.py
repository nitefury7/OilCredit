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


class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.SmallIntegerField(choices=Gender.choices)
    city = models.CharField(max_length=20, blank=True)
    state = models.CharField(max_length=20, blank=True)
    zip_code = models.BigIntegerField(blank=True, null=True)
    contact = PhoneNumberField(blank=True)

    def __str__(self):
        return str(self.user.username)


class Invoice(models.Model):
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    order_timestamp = models.DateTimeField()
    employee = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.CASCADE, blank=True, null=True,
    )

    def cost(self):
        purchases = Purchase.objects.filter(invoice=self)
        return sum(purchase.cost() for purchase in purchases)

    def __str__(self):
        return f"{self.customer.user.username} - {self.employee.user.username}"


class Purchase(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    volume = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    rate = models.FloatField(validators=(MinValueValidator(0), ))

    def cost(self):
        return self.volume * self.rate

    def __str__(self):
        return f"{self.volume} {self.item.name} at {self.rate}"

from ssl import OP_NO_COMPRESSION
from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.
class EmployeeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    gender = models.CharField(max_length=1, choices = (('M', 'Male'), ('F', 'Female'), ('O', 'Other')))
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    zip_code = models.BigIntegerField()
    contact = PhoneNumberField()
    employee_type = models.CharField(max_length=1, choices = (('T', 'Temporary'), ('P', 'Permanent'),))
    employment_date = models.DateField()
    post = models.CharField(max_length=20)
    
    def __str__(self):
        return f"{self.user.username}"


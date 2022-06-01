from tkinter import W
from django.core.management.base import BaseCommand
from customer.models import Item, CustomerProfile
from employee.models import EmployeeProfile
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone


class Command(BaseCommand):
    help = 'This command populates the database with default db'

    def handle(self, *_, **__):
        self.create_super_user(username='ayush', password='ayush')
        self.create_customer({
            "username": "customer",
            "password": "ayush123",
            "first_name": "Member",
            "last_name": "Rebmem",
            "email": "member@example.com",
            "gender": 0,
            "city": "Kathmandu",
            "state": "Bagmati",
            "zip_code": "44600",
            "contact": "+9779876543210",
        })
        self.create_employee({
            "username": "employee",
            "password": "ayush123",
            "first_name": "Employee",
            "last_name": "Eeyolpme",
            "email": "employee@example.com",
            "gender": 0,
            "city": "Kathmandu",
            "state": "Bagmati",
            "zip_code": "44600",
            "contact": "+9779876543210",
            "employment_date": timezone.now(),
            "employee_type": 0,
            "post": "Manager",
        })
        self.create_items()

    def create_items(self):
        items = (
            {'name': 'PLUS', 'description': '', 'rate': 2.0},
            {'name': 'UNLD', 'description': '', 'rate': 2.5},
            {'name': 'SUPER', 'description': '', 'rate': 2.2},
            {'name': 'DIESEL', 'description': '', 'rate': 1.8},
            {'name': 'R/DIESEL', 'description': '', 'rate': 2.7},
            {'name': 'OIL', 'description': '', 'rate': 2.3},
            {'name': 'MISC.', 'description': '', 'rate': 2.3},
        )
        for item in items:
            if not Item.objects.filter(name=item['name']).exists():
                Item(**item).save()
                self.stdout.write(self.style.SUCCESS(f"Added {item['name']}"))

    def create_customer(self, details):
        if not User.objects.filter(username=details["username"]).exists():
            user = User.objects.create_user(
                details["username"], password=details["password"])
            user.first_name = details["first_name"]
            user.last_name = details["last_name"]
            user.email = details["email"]
            profile = CustomerProfile.objects.create(
                user=user, gender=details['gender'])
            profile.city = details['city']
            profile.state = details['state']
            profile.zip_code = details['zip_code']
            profile.contact = details['contact']

            with transaction.atomic():
                user.save()
                profile.save()

            self.stdout.write(self.style.SUCCESS(
                f"Created customer '{details['username']}', with password '{details['password']}'"))

    def create_employee(self, details):
        if not User.objects.filter(username=details["username"]).exists():
            user = User.objects.create_user(
                details["username"], password=details["password"])
            user.first_name = details["first_name"]
            user.last_name = details["last_name"]
            user.email = details["email"]
            profile = EmployeeProfile.objects.create(
                user=user, gender=details['gender'],
                employment_date=details['employment_date'],
                employee_type=details['employee_type']
            )
            profile.city = details['city']
            profile.state = details['state']
            profile.zip_code = details['zip_code']
            profile.contact = details['contact']
            profile.post = details['post']

            with transaction.atomic():
                user.save()
                profile.save()

            self.stdout.write(self.style.SUCCESS(
                f"Created employee '{details['username']}', with password '{details['password']}'"))

    def create_super_user(self, username, password):
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(username, password=password)
            user.is_superuser = True
            user.is_staff = True
            user.save()
            self.stdout.write(self.style.SUCCESS(
                f"Created superuser '{username}', with password '{password}'"))

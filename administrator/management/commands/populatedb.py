from datetime import timedelta
import random

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

from customer.models import Item, CustomerProfile, Invoice, Purchase
from employee.models import EmployeeProfile
from home.utils import get_profile


class Command(BaseCommand):
    help = 'This command populates the database with default db'

    def handle(self, *_, **__):
        PASSWORD = "ayush123"
        NUM_EMPLOYEES = 5
        NUM_CUSTOMERS = 5
        NUM_TRANSACTIONS = 20

        self.create_items()
        self.create_super_user(username='admin', password='admin')

        employees = []
        for i in range(NUM_EMPLOYEES):
            employee_details = self.create_random_employee_details(
                f"employee{i}", PASSWORD)
            employees.append(self.create_employee(employee_details))

        customers = []
        for i in range(NUM_CUSTOMERS):
            customer_details = self.create_random_customer_details(
                f"customer{i}", PASSWORD)
            customers.append(self.create_customer(customer_details))

        for customer in customers:
            for employee in employees:
                self.create_random_transactions(
                    customer=customer, employee=employee, size=NUM_TRANSACTIONS)

    def create_random_employee_details(self, username, password):
        return {
            "username": username,
            "password": password,
            "first_name": username,
            "last_name": username[::-1],
            "email": f"{username}@example.com",
            "gender": 0,
            "city": "Kathmandu",
            "state": "Bagmati",
            "zip_code": "44600",
            "contact": "+9779876543210",
            "employment_date": timezone.now(),
            "employee_type": 0,
            "post": "Manager",
        }

    def create_random_customer_details(self, username, password):
        return {
            "username": username,
            "password": password,
            "first_name": username,
            "last_name": username[::-1],
            "email": f"{username}@example.com",
            "gender": 0,
            "city": "Kathmandu",
            "state": "Bagmati",
            "zip_code": "44600",
            "contact": "+9779876543210",
        }

    def create_items(self):
        items = (
            {'name': 'PLUS', 'description': ''},
            {'name': 'UNLD', 'description': ''},
            {'name': 'SUPER', 'description': ''},
            {'name': 'DIESEL', 'description': ''},
            {'name': 'R/DIESEL', 'description': ''},
            {'name': 'OIL', 'description': ''},
            {'name': 'MISC.', 'description': ''},
        )
        ret = []
        for item in items:
            if not Item.objects.filter(name=item['name']).exists():
                i = Item(**item)
                i.save()
                ret.append(i)
                self.stdout.write(self.style.SUCCESS(f"Added {item['name']}"))
        return ret

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
            return user
        return User.objects.get(username=details['username'])

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
            return user
        return User.objects.get(username=details['username'])

    def create_super_user(self, username, password):
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(username, password=password)
            user.is_superuser = True
            user.is_staff = True
            user.save()
            self.stdout.write(self.style.SUCCESS(
                f"Created superuser '{username}', with password '{password}'"))
            return user
        return User.objects.get(username=username)

    def create_random_transactions(self, customer, employee, size=1):
        for _ in range(size):
            invoice = self.create_invoice({
                'customer': customer,
                'employee': employee,
                'order_timestamp': timezone.now() - timedelta(days=random.randint(0, 10))
            })

            for item in random.sample(list(Item.objects.all()), 5):
                self.create_purchase({
                    'invoice': invoice,
                    'item': item,
                    'volume': random.randint(1, 10),
                    'total': random.uniform(300, 1000),
                })
        self.stdout.write(self.style.SUCCESS(f"Created {size} random invoice"))

    def create_invoice(self, details):
        customer = get_profile(CustomerProfile, details['customer'])
        employee = get_profile(EmployeeProfile, details['employee'])
        if customer and employee:
            invoice = Invoice.objects.create(
                customer=customer,
                employee=employee,
                order_timestamp=details['order_timestamp'],
            )
            invoice.save()
            return invoice

    def create_purchase(self, details):
        purchase = Purchase.objects.create(
            invoice=details['invoice'],
            item=details['item'],
            volume=details['volume'],
            total=details['total'],
        )
        purchase.save()
        return purchase

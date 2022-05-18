from django.core.management.base import BaseCommand
from customer.models import Item


class Command(BaseCommand):
    help = 'This command populates the database with default db'

    def handle(self, *_, **__):
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

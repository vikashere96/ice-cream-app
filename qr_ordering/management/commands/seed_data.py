from django.core.management.base import BaseCommand
from qr_ordering.models import IceCream, Table

class Command(BaseCommand):
    help = 'Seeds the database with initial data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')

        # Clear existing data
        IceCream.objects.all().delete()
        Table.objects.all().delete()

        # Create Ice Creams
        ice_creams = [
            {'name': 'Kesar Pista', 'price': 120.00},
            {'name': 'Mango', 'price': 150.00},
            {'name': 'Paan', 'price': 130.00},
            {'name': 'Gulkand', 'price': 130.00},
            {'name': 'Tender Coconut', 'price': 160.00},
        ]
        for ice_cream_data in ice_creams:
            IceCream.objects.create(**ice_cream_data)
        
        # Create Tables
        for i in range(1, 6):
            Table.objects.create(number=i)

        self.stdout.write(self.style.SUCCESS('Successfully seeded data!')) 
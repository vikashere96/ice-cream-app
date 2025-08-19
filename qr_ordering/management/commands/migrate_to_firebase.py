from django.core.management.base import BaseCommand
from qr_ordering.models import IceCream, Table
from qr_ordering.firebase_utils import upload_file_to_firebase_storage
from firebase_admin import db
import os

class Command(BaseCommand):
    help = 'Migrate existing IceCream and Table images/data to Firebase Storage and Database.'

    def handle(self, *args, **options):
        self.migrate_icecreams_to_firebase()
        self.migrate_tables_to_firebase()
        self.stdout.write(self.style.SUCCESS('Migration complete.'))

    def migrate_icecreams_to_firebase(self):
        for icecream in IceCream.objects.all():
            if icecream.image:
                image_url = icecream.image.url  # Local media URL
                db.reference(f'products/{icecream.id}').set({
                    'name': icecream.name,
                    'price': float(icecream.price),
                    'image_url': image_url
                })
                self.stdout.write(f"IceCream {icecream.name} migrated.")

    def migrate_tables_to_firebase(self):
        for table in Table.objects.all():
            if table.qr_code:
                qr_code_url = table.qr_code.url  # Local media URL
                db.reference(f'tables/{table.id}').set({
                    'number': table.number,
                    'token': str(table.token),
                    'qr_code_url': qr_code_url
                })
                self.stdout.write(f"Table {table.number} migrated.")

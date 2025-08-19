from qr_ordering.models import IceCream, Table
from qr_ordering.firebase_utils import upload_file_to_firebase_storage
from firebase_admin import db
import os

def migrate_icecreams_to_firebase():
    for icecream in IceCream.objects.all():
        if icecream.image and os.path.exists(icecream.image.path):
            firebase_path = f"ice_cream_images/{os.path.basename(icecream.image.name)}"
            image_url = upload_file_to_firebase_storage(icecream.image.path, firebase_path)
            db.reference(f'products/{icecream.id}').set({
                'name': icecream.name,
                'price': float(icecream.price),
                'image_url': image_url
            })
            print(f"IceCream {icecream.name} migrated.")

def migrate_tables_to_firebase():
    for table in Table.objects.all():
        if table.qr_code and os.path.exists(table.qr_code.path):
            firebase_path = f"qr_codes/{os.path.basename(table.qr_code.name)}"
            qr_url = upload_file_to_firebase_storage(table.qr_code.path, firebase_path)
            db.reference(f'tables/{table.id}').set({
                'number': table.number,
                'token': str(table.token),
                'qr_code_url': qr_url
            })
            print(f"Table {table.number} migrated.")

if __name__ == "__main__":
    migrate_icecreams_to_firebase()
    migrate_tables_to_firebase()
    print("Migration complete.")

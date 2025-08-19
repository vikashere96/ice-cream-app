from qr_ordering.models import Table

NEW_BASE_URL = "https://6da97e8fbc3c.ngrok-free.app/"

def update_all_tables_qr_base_url():
    for table in Table.objects.all():
        table.qr_base_url = NEW_BASE_URL
        table.qr_code = None  # Force QR regeneration
        table.save()
        print(f"Updated Table {table.number} QR code to new base URL.")

if __name__ == "__main__":
    update_all_tables_qr_base_url()
    print("All tables updated.")

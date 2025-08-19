from django.core.management.base import BaseCommand
from django.conf import settings
from qr_ordering.models import Table
import os
import json
from urllib.request import urlopen
from urllib.error import URLError


class Command(BaseCommand):
    help = 'Update all tables to use the new QR base URL and regenerate QR codes.'

    def add_arguments(self, parser):
        parser.add_argument('--base-url', dest='base_url', default=None, help='Base URL e.g., https://abc.ngrok-free.app')
        parser.add_argument('--auto-ngrok', action='store_true', help='Auto-detect ngrok HTTPS URL from local API (http://127.0.0.1:4040)')

    def handle(self, *args, **options):
        base_url = options.get('base_url') or os.environ.get('SITE_BASE_URL') or getattr(settings, 'SITE_BASE_URL', 'http://127.0.0.1:8000')

        if options.get('auto_ngrok'):
            try:
                with urlopen('http://127.0.0.1:4040/api/tunnels') as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                tunnels = data.get('tunnels', []) if isinstance(data, dict) else []
                https_tunnels = [t for t in tunnels if str(t.get('public_url', '')).startswith('https://')]
                http_tunnels = [t for t in tunnels if str(t.get('public_url', '')).startswith('http://')]
                chosen = (https_tunnels[0] if https_tunnels else (http_tunnels[0] if http_tunnels else None))
                if chosen:
                    base_url = chosen.get('public_url')
                    self.stdout.write(self.style.SUCCESS(f"Detected ngrok URL: {base_url}"))
                else:
                    self.stdout.write(self.style.WARNING('No active ngrok tunnels found; falling back to provided/base URL'))
            except URLError as e:
                self.stdout.write(self.style.WARNING(f'Failed to query ngrok API: {e}. Falling back to provided/base URL'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Unexpected error reading ngrok API: {e}. Falling back to provided/base URL'))
        base_url = base_url.rstrip('/') + '/'
        updated = 0
        for table in Table.objects.all():
            table.qr_base_url = base_url
            # Trigger regeneration by clearing and saving
            table.qr_code = None
            table.save()
            updated += 1
            self.stdout.write(self.style.SUCCESS(f"Updated Table {table.number} QR code -> {base_url}"))
        self.stdout.write(self.style.SUCCESS(f"All tables updated. Total: {updated}"))

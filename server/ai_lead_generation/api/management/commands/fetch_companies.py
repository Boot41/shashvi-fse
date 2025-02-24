import requests

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Fetch companies from an external API'

    def handle(self, *args, **options):
        # Placeholder for fetching logic
        self.stdout.write(self.style.SUCCESS('Successfully fetched companies'))

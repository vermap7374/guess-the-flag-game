import requests
from django.core.management.base import BaseCommand
from game.models import Country

class Command(BaseCommand):
    help = 'Fetch country data from REST Countries API and save to database'

    def handle(self, *args, **kwargs):
        url = "https://restcountries.com/v3.1/all"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            Country.objects.all().delete()  # Clear existing data

            for country in data:
                name = country.get('name', {}).get('common', '')
                flag_url = country.get('flags', {}).get('png', '')

                if name and flag_url:
                    Country.objects.create(name=name, flag_url=flag_url)

            self.stdout.write(self.style.SUCCESS('Successfully imported country data!'))
        else:
            self.stdout.write(self.style.ERROR('Failed to fetch country data'))

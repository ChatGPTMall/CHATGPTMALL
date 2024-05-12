import os

from django.core.files import File
from django.core.management.base import BaseCommand
import openpyxl

from engine.models import Community


class Command(BaseCommand):
    help = 'Imports data from an Excel file'

    def handle(self, *args, **kwargs):
        # Path to your Excel file
        path_to_excel = 'Benny.xlsx'

        # Load the workbook and get the first sheet
        workbook = openpyxl.load_workbook(path_to_excel)
        sheet = workbook.active

        Community.objects.all().delete()

        # Open the image file once, to be used for all records
        with open("logo.jpg", 'rb') as image_file:
            django_file = File(image_file, name=os.path.basename("logo.jpg"))
            # Iterate over the rows and process each
            for row in sheet.iter_rows(min_row=2):  # Skip the header row
                name = row[0].value
                new_community_name = row[1].value
                community_id = row[2].value

                community = Community.objects.create(name=new_community_name, community_id=community_id)
                community.logo = django_file
                community.save()

                self.stdout.write(self.style.SUCCESS(f'Created: {new_community_name}'))

        self.stdout.write(self.style.SUCCESS('Finished importing data.'))

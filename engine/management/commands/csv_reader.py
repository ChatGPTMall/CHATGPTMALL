import openpyxl
from django.core.management import BaseCommand

from engine.models import Industries, Capabilities, Jobs
# Load the xlsx file
workbook = openpyxl.load_workbook('capabilities.xlsx')
sheet = workbook.active

class Command(BaseCommand):
    help = 'Upload Marketing Data'

    def handle(self, *args, **options):
        for row in sheet.iter_rows(min_row=2, values_only=True):
            # try:
            #     if row[0] and row[1]:
            #         Industries.objects.create(title=row[0], slogan=row[1])
            # except Exception as e:
            #     continue
            # try:
            #     if row[1] and row[2]:
            #         job = row[1]
            #         slogan = row[2].split(". ")[1]
            #         Jobs.objects.create(title=job, slogan=slogan)
            # except Exception as e:
            #     continue
            try:
                if row[0] and row[1]:
                    Capabilities.objects.create(title=row[0], slogan=row[1])
            except Exception as e:
                continue




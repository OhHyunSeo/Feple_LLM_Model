from django.core.management.base import BaseCommand
from apps.consultlytics.models import Consulting

class Command(BaseCommand):
    help = 'Print all call_id values in Consulting table.'

    def handle(self, *args, **kwargs):
        call_ids = list(Consulting.objects.values_list('call_id', flat=True))
        if call_ids:
            self.stdout.write(self.style.SUCCESS(f'Consulting call_ids: {call_ids}'))
        else:
            self.stdout.write(self.style.WARNING('No Consulting data found.')) 
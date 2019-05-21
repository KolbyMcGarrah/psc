from django.core.management.base import BaseCommand, CommandError
from accounts.models import credits

class Command(BaseCommand):
    def handle(self,*args,**options):
        print('updating expiring credits')
        credits.expiringCredits()
        print('updating expired credits')
        credits.expireCredits()
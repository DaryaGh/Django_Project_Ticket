from django.core.management import BaseCommand

from Tickets.models import Category


class Command(BaseCommand):

    help = 'Reset Is_active_categories_one_to_zero attribute table'

    def handle(self, *args, **options):
        Category.objects.filter(is_active=False).update(is_active=True)

        self.stdout.write(self.style.SUCCESS("\nAll Categories Updated !!!\n"))
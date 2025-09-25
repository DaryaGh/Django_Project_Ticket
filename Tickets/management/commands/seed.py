from django.core.management import BaseCommand


class Command(BaseCommand):

    help = 'Concatenate'

    def add_arguments(self, parser):
        parser.add_argument(
            '--name',
            type=str,
            help='Concatenate',
            default='Ali',
        )
        parser.add_argument(
            '--family',
            type=str,
            help='Concatenate',
            default='Karimi',
        )

    def handle(self, *args, **options):
        s= options['name']
        s += options['family']

        self.stdout.write(self.style.SUCCESS(s))
from django.core.management import BaseCommand
import random

class Command(BaseCommand):

    help = 'Generate a random two-digit integer number'

    def add_arguments(self, parser):
        # Optional:add arguments if needed
        parser.add_argument(
            '--count',
            type=int,
            help='The random two-digit integer number (default:1)',
            default=1,
        )

    def handle(self, *args, **options):
        count = options['count']

        for i in range(count):
            random_number = random.randint(10, 99)
            self.stdout.write(self.style.SUCCESS(f'Random two-digit number: {random_number}'))

            if count > 1 and i < count - 1:
                self.stdout.write('----')

# اموزشی است و برای تمرین کپی میشود پشت هم دیگ
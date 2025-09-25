from django.core.management import BaseCommand

from Tickets.factories import *

class Command(BaseCommand):
    help = 'Seeds database with sample data'

    def add_arguments(self, parser):
        # parser.add_argument('--users', nargs='+', type=int ,default=1,help='Number of users to seed')
        parser.add_argument('--categories', type=int ,default=1,help='Number of categories to seed')
        parser.add_argument('--tags', type=int ,default=5,help='Number of tags to seed')
        # parser.add_argument('--tickets', type=int ,default=1,help='Number of tickets to seed')
        # parser.add_argument('--assignments', type=int ,default=1,help='Number of assignments to seed')


    def handle(self, *args, **options):
        # users = UserFactory.create_batch(options['users'])
        categories = CategoryFactory.create_batch(options['categories'])
        tags = TagFactory.create_batch(options['tags'])
        # tickets = TicketFactory.create_batch(options['tickets'])
        # assignments = AssignmentFactory.create_batch(options['assignments'])

        # for  ticket in tickets:
        #     # ticket.tags.add(*TagFactory.create_batch(options['tags']))
        #     ticket.tags.add(*TagFactory.create_batch(2))


        self.stdout.write(self.style.SUCCESS('\nDatabase seeded successfully!\n'))

        # self.stdout.write(self.style.SUCCESS(f'{len(users)} users added!\n'))
        self.stdout.write(self.style.SUCCESS(f'{len(categories)} categories added!\n'))
        self.stdout.write(self.style.SUCCESS(f'{len(tags)} tags added!\n'))
        # self.stdout.write(self.style.SUCCESS(f'{len(tickets)} tags added!\n'))
        # self.stdout.write(self.style.SUCCESS(f'{len(assignments)} tags added!\n'))

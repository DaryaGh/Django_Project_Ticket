from django.core.management import BaseCommand, CommandError, call_command
from django.db import connection
from django.db.migrations.recorder import MigrationRecorder
# from django.core.management import call_command

class Command(BaseCommand):
    help = "Laravel-Like migration helper for Rollback , Reset , Status"

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='action',help='Action to perform')
        rollback_parser = subparsers.add_parser('rollback', help='Rollback migration')
        rollback_parser.add_argument(
            '--steps',
            type=int,
            default=1,
            help='Number of migration steps to rollback',
        )

        rollback_table_parser = subparsers.add_parser('rollback_table', help='Rollback migration')
        rollback_table_parser.add_argument(
            '--steps',
            type=int,
            default=1,
            help='Number of migration steps to rollback',
        )


        subparsers.add_parser('reset', help='Reset all migrations')

        subparsers.add_parser('status', help='Show migration status')

    def handle(self, *args, **options):
        action = options['action']
        if action == 'rollback':
            self.rollback(steps=options['steps'])
        elif action == 'rollback_table':
            self.rollback_table(steps=options['steps'])
        elif action == 'reset':
            self.reset()
        elif action == 'status':
            self.status()
        else:
            raise CommandError('Invalid action. Choose rollback or reset , or status.')

    def rollback(self, steps=1):
        applied = MigrationRecorder.Migration.objects.all().order_by('-applied')
        if not applied.exists():
            self.stdout.write('No migrations applied')
            return

        apps_seen = []
        migrations_to_rollback = []
        for mig in applied:
            if mig.app not in apps_seen:
                apps_seen.append(mig.app)
            if len(apps_seen) > steps:
                break
            migrations_to_rollback.append((mig.app,mig.name))

        for app,name in migrations_to_rollback:
            self.stdout.write(f'Rolling back migration for {app} -> {name} ...')
            call_command('migrate', app,name)

    def rollback_table(self, steps=1):
        recorder = MigrationRecorder(connection)
        applied_migrations = recorder.applied_migrations()

        if not applied_migrations:
            self.stdout.write('No migrations applied')
            return

        # مرتب سازی بر اساس تاریخ اعمال (جدیدترین اول)
        sorted_migrations = sorted(applied_migrations, key=lambda x: x[1], reverse=True)

        # فقط migrations مربوط به apps کاربردی (نه apps داخلی Django)
        user_migrations = [mig for mig in sorted_migrations
                           if mig[0] not in ['admin', 'auth', 'contenttypes', 'sessions']]

        migrations_to_rollback = user_migrations[:steps]

        for app, mig_name in migrations_to_rollback:
            self.stdout.write(f'Rolling back migration for {app} -> {mig_name} ...')

            # روش صحیح: مهاجرت به migration قبلی
            try:
                # پیدا کردن migration قبلی
                call_command('migrate', app, 'zero', verbosity=1)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error rolling back {app}: {e}'))

    def reset(self):
        recorder = MigrationRecorder.Migration.objects.all()
        apps = recorder.values_list('app', flat=True).distinct()
        for app in apps:
            self.stdout.write(f'Resetting migration for {app} ...')
            call_command('migrate', app,"Zero")

# معادل است با showmigration
    def status(self):
        call_command('showmigrations')


# from django.core.management import BaseCommand, CommandError, call_command
# from django.db import connection
# from django.db.migrations.recorder import MigrationRecorder
#
#
# class Command(BaseCommand):
#     help = "Laravel-Like migration helper for Rollback , Reset , Status"
#
#     def add_arguments(self, parser):
#         subparsers = parser.add_subparsers(dest='action', help='Action to perform')
#
#         rollback_parser = subparsers.add_parser('rollback', help='Rollback migration')
#         rollback_parser.add_argument(
#             '--steps',
#             type=int,
#             default=1,
#             help='Number of migration steps to rollback',
#         )
#
#         subparsers.add_parser('reset', help='Reset all migrations')
#         subparsers.add_parser('status', help='Show migration status')
#
#     def handle(self, *args, **options):
#         action = options['action']
#         if action == 'rollback':
#             self.rollback(steps=options['steps'])
#         elif action == 'reset':
#             self.reset()
#         elif action == 'status':
#             self.status()
#         else:
#             raise CommandError('Invalid action. Choose rollback or reset , or status.')
#
#     # def rollback(self, steps=1):
#     #     # ایجاد instance از MigrationRecorder
#     #     recorder = MigrationRecorder(connection)
#     #     applied_migrations = recorder.applied_migrations()
#     #
#     #     if not applied_migrations:
#     #         self.stdout.write('No migrations applied')
#     #         return
#     #
#     #     apps_seen = []
#     #     migrations_to_rollback = []
#     #
#     #     for mig in sorted(applied_migrations, key=lambda x: x[1], reverse=True):
#     #         app_name, mig_name = mig
#     #         if app_name not in apps_seen:
#     #             apps_seen.append(app_name)
#     #         if len(apps_seen) > steps:
#     #             break
#     #         migrations_to_rollback.append((app_name, mig_name))
#     #
#     #     for app, name in migrations_to_rollback:
#     #         self.stdout.write(f'Rolling back migration for {app} -> {name} ...')
#     #         # باید به migration قبلی برگردیم
#     #         call_command('migrate', app, name, verbosity=0)
#
#     def rollback(self, steps=1):
#         recorder = MigrationRecorder(connection)
#         applied_migrations = recorder.applied_migrations()
#
#         if not applied_migrations:
#             self.stdout.write('No migrations applied')
#             return
#
#         # مرتب سازی بر اساس تاریخ اعمال (جدیدترین اول)
#         sorted_migrations = sorted(applied_migrations, key=lambda x: x[1], reverse=True)
#
#         # فقط migrations مربوط به apps کاربردی (نه apps داخلی Django)
#         user_migrations = [mig for mig in sorted_migrations
#                            if mig[0] not in ['admin', 'auth', 'contenttypes', 'sessions']]
#
#         migrations_to_rollback = user_migrations[:steps]
#
#         for app, mig_name in migrations_to_rollback:
#             self.stdout.write(f'Rolling back migration for {app} -> {mig_name} ...')
#
#             # روش صحیح: مهاجرت به migration قبلی
#             try:
#                 # پیدا کردن migration قبلی
#                 call_command('migrate', app, 'zero', verbosity=1)
#             except Exception as e:
#                 self.stdout.write(self.style.ERROR(f'Error rolling back {app}: {e}'))
#
#     def reset(self):
#         # ایجاد instance از MigrationRecorder
#         recorder = MigrationRecorder(connection)
#         applied_migrations = recorder.applied_migrations()
#
#         apps = set()
#         for mig in applied_migrations:
#             apps.add(mig[0])  # app name
#
#         for app in apps:
#             self.stdout.write(f'Resetting migration for {app} ...')
#             try:
#                 # استفاده از "zero" به جای "Zero"
#                 call_command('migrate', app, "zero", verbosity=1)
#             except Exception as e:
#                 self.stdout.write(self.style.ERROR(f'Error resetting {app}: {e}'))
#
#     def status(self):
#         call_command('showmigrations')

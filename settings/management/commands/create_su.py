# ساخت سریع تر create super user admin
from django.contrib.auth.models import User
from django.core.management import BaseCommand



class Command(BaseCommand):
    help = 'Create a SuperUser non-interactively'

    def handle(self, *args, **options):
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@gmail.com", "admin")
            self.stdout.write(self.style.SUCCESS('Successfully created a SuperUser'))
        else:
            self.stdout.write(self.style.WARNING('SuperUser already exists'))
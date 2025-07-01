from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Creates a superadmin user at the start if it does not exist'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        email = "admin@gmail.com"
        password = "12345"
        full_name = "Admin User"

        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(
                email=email,
                password=password,
                full_name=full_name
            )
            self.stdout.write(self.style.SUCCESS(f'Superadmin created: {email}'))
        else:
            self.stdout.write(self.style.WARNING(f'Superadmin already exists: {email}'))
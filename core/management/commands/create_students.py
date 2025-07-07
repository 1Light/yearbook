from django.core.management.base import BaseCommand
from core.models import User, StudentProfile
from django.utils.crypto import get_random_string

class Command(BaseCommand):
    help = 'Create 50 student users and profiles'

    def handle(self, *args, **kwargs):
        # Assume there is at least one encoder user who created these students
        encoder = User.objects.filter(role='encoder').first()
        if not encoder:
            self.stdout.write(self.style.ERROR("No encoder user found. Create at least one encoder first."))
            return

        for i in range(1, 51):
            email = f'student{i}@gmail.com'
            if User.objects.filter(email=email).exists():
                self.stdout.write(self.style.WARNING(f"User {email} already exists. Skipping."))
                continue

            full_name = f"Student {i}"
            user = User.objects.create_user(
                email=email,
                password='studentpass123',
                role='student',
                full_name=full_name
            )

            # Minimal required fields, customize as needed
            StudentProfile.objects.create(
                user=user,
                department="Computer Science",
                university="Addis Ababa University",
                graduation_year=2025,
                quote=f"This is a quote from {full_name}",
                best_memory=f"My best memory is number {i}",
                bio=f"This is the bio for {full_name}.",
                created_by=encoder
            )

            self.stdout.write(self.style.SUCCESS(f"Created student {email}"))
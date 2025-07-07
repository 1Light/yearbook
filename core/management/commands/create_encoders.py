from django.core.management.base import BaseCommand
from core.models import User, EncoderProfile

class Command(BaseCommand):
    help = 'Create 3 encoder users, one for each encoder type'

    def handle(self, *args, **kwargs):
        try:
            superadmin = User.objects.get(email='admin@gmail.com', role='superadmin')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("Superadmin with email admin@gmail.com does not exist."))
            return

        encoders_data = [
            {
                'email': 'encoder1@gmail.com',
                'full_name': 'Encoder One',
                'type': 1,
                'notes': 'Handles student registration',
            },
            {
                'email': 'encoder2@gmail.com',
                'full_name': 'Encoder Two',
                'type': 2,
                'notes': 'Handles games',
            },
            {
                'email': 'encoder3@gmail.com',
                'full_name': 'Encoder Three',
                'type': 3,
                'notes': 'Handles videos and images',
            },
        ]

        for data in encoders_data:
            if not User.objects.filter(email=data['email']).exists():
                encoder = User.objects.create_encoder(
                    email=data['email'],
                    password='pass123',
                    full_name=data['full_name']
                )
                EncoderProfile.objects.create(
                    user=encoder,
                    phone_number='0911000000',
                    university='Addis Ababa University',
                    department='Computer Science',
                    additional_notes=data['notes'],
                    encoder_type=data['type'],
                    created_by=superadmin
                )
                self.stdout.write(self.style.SUCCESS(f"Created encoder: {data['email']}"))
            else:
                self.stdout.write(self.style.WARNING(f"Encoder already exists: {data['email']}"))

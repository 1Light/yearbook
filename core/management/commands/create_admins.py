from django.core.management.base import BaseCommand
from core.models import User, AdminProfile

class Command(BaseCommand):
    help = 'Create 3 admin users, one for each institution type (highschool, college, university)'

    def handle(self, *args, **kwargs):
        try:
            superadmin = User.objects.get(email='admin@gmail.com', role='superadmin')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("Superadmin with email admin@gmail.com does not exist."))
            return

        admins_data = [
            {
                'email': 'highschool_admin@gmail.com',
                'full_name': 'High School Admin',
                'role': 'highschool_admin',
                'institution_type': 'highschool',
                'institution_name': 'Unity High School',
            },
            {
                'email': 'college_admin@gmail.com',
                'full_name': 'College Admin',
                'role': 'college_admin',
                'institution_type': 'college',
                'institution_name': 'St. Mary’s College',
            },
            {
                'email': 'university_admin@gmail.com',
                'full_name': 'University Admin',
                'role': 'university_admin',
                'institution_type': 'university',
                'institution_name': 'Addis Ababa University',
            },
        ]

        for data in admins_data:
            if not User.objects.filter(email=data['email']).exists():
                admin_user = User.objects.create_admin(
                    email=data['email'],
                    password='subadminpass123',
                    role=data['role'],
                    full_name=data['full_name'],
                    institution_type=data['institution_type'],
                    institution_name=data['institution_name'],
                    created_by=superadmin
                )
                AdminProfile.objects.create(
                    user=admin_user,
                    institution_type=data['institution_type'],
                    institution_name=data['institution_name'],
                    created_by=superadmin
                )
                self.stdout.write(self.style.SUCCESS(f"Created admin: {data['email']}"))
            else:
                self.stdout.write(self.style.WARNING(f"Admin already exists: {data['email']}"))
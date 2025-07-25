from django.core.management.base import BaseCommand
from django.utils import timezone
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings

from core.models import StudentProfile
from student.models import RSVPToken

class Command(BaseCommand):
    help = "Send RSVP reminder emails to students"

    def handle(self, *args, **kwargs):
        today = timezone.now().date()

        domain = getattr(settings, 'FRONTEND_DOMAIN', 'https://digital-yearbook-backend.onrender.com')

        for student in StudentProfile.objects.filter(status='approved', rsvp=False):
            if not student.graduation_year:
                continue

            reunion_date = timezone.datetime(student.graduation_year + 10, 6, 30, tzinfo=timezone.utc)
            days_left = (reunion_date.date() - today).days

            if days_left in [30, 7, 3, 1]:
                token, created = RSVPToken.objects.get_or_create(user=student.user)
                rsvp_link = reverse("rsvp_prompt", args=[token.token])
                full_link = f"{domain}{rsvp_link}"

                send_mail(
                    subject="RSVP for Your Reunion",
                    message=f"Hi {student.user.full_name}, your reunion is in {days_left} days! Please RSVP here: {full_link}",
                    from_email="no-reply@reunionmail.com",
                    recipient_list=[student.user.email],
                    fail_silently=False,
                )

                self.stdout.write(f"Sent RSVP email to {student.user.email}")
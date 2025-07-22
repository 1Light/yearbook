from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.timezone import make_aware
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings

from datetime import datetime, timezone as dt_timezone

from core.models import StudentProfile
from student.models import RSVPToken

class Command(BaseCommand):
    help = "Send RSVP reminder emails to students"

    def handle(self, *args, **kwargs):
        today = timezone.now()
        self.stdout.write(f"[DEBUG] Current UTC time: {today}")

        domain = getattr(settings, 'FRONTEND_DOMAIN', 'https://digital-yearbook-backend.onrender.com')
        self.stdout.write(f"[DEBUG] Using domain: {domain}")

        students = StudentProfile.objects.filter(status='approved', rsvp=False)
        self.stdout.write(f"[DEBUG] Found {students.count()} students to check")

        for student in students:
            if not student.graduation_year:
                self.stdout.write(f"[DEBUG] Skipping student {student.user.email}: no graduation_year")
                continue

            naive_reunion_date = datetime(student.graduation_year + 10, 6, 30)
            reunion_date = make_aware(naive_reunion_date, dt_timezone.utc)
            """ days_left = (reunion_date.date() - today.date()).days """
            days_left = 3  # For testing purposes, set to 3 days left
            self.stdout.write(f"[DEBUG] Student {student.user.email}: days_left={days_left}")

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
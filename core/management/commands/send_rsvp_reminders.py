from django.core.management.base import BaseCommand
from django.utils import timezone
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timezone as dt_timezone, timedelta

from core.models import StudentProfile
from student.models import RSVPToken

class Command(BaseCommand):
    help = "Send RSVP reminder emails to students"

    def handle(self, *args, **kwargs):
        now = datetime.now(dt_timezone.utc)  # Use timezone.now() once for consistency
        self.stdout.write(f"[DEBUG] Current UTC time: {now}")

        domain = getattr(settings, 'FRONTEND_DOMAIN', 'https://digital-yearbook-backend.onrender.com')
        self.stdout.write(f"[DEBUG] Using domain: {domain}")

        students = StudentProfile.objects.filter(status='approved', rsvp=False)
        self.stdout.write(f"[DEBUG] Found {students.count()} students to check")

        for student in students:
            if not student.graduation_year:
                self.stdout.write(f"[DEBUG] Skipping student {student.user.email}: no graduation_year")
                continue

            reunion_date = now + timedelta(minutes=7)  # For testing purposes
            time_left = reunion_date - now
            minutes_left = int(time_left.total_seconds() // 60)
            minutes_left = 3
            self.stdout.write(f"[DEBUG] Student {student.user.email}: minutes_left={minutes_left}")

            if minutes_left in [4, 3, 2, 1]:
                token, created = RSVPToken.objects.get_or_create(user=student.user)
                rsvp_link = reverse("rsvp_prompt", args=[token.token])  # e.g. '/rsvp/<uuid>/'
                full_link = f"{domain}/api/student{rsvp_link}"  # Prepend api/student as needed
                self.stdout.write(f"[DEBUG] RSVP link: {full_link}")

                try:
                    send_mail(
                        subject="RSVP for Your Reunion",
                        message=f"Hi {student.user.full_name}, your reunion is in {minutes_left} minutes! Please RSVP here: {full_link}",
                        from_email=settings.EMAIL_FROM,
                        recipient_list=[student.user.email],
                        fail_silently=False,
                    )
                    self.stdout.write(f"[SUCCESS] Sent RSVP email to {student.user.email}")
                except Exception as e:
                    self.stderr.write(f"[ERROR] Failed to send email to {student.user.email}: {e}")
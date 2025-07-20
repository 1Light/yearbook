from django.shortcuts import render, get_object_or_404
from datetime import datetime, timezone as dt_timezone
from .models import RSVPToken

from rest_framework.response import Response
from rest_framework import status
from core.models import StudentProfile

import logging
logger = logging.getLogger(__name__)

import os
from django.views.decorators.csrf import csrf_exempt
from django.core.management import call_command
from django.http import HttpResponse, HttpResponseForbidden
from rest_framework.views import APIView

from django.conf import settings

@csrf_exempt
def run_rsvp_reminders(request):
    token = request.GET.get('token')
    if token != settings.RSVP_SECRET_TOKEN:
        return HttpResponseForbidden("Forbidden: Invalid token")

    call_command('send_rsvp_reminders')
    return HttpResponse("RSVP reminders sent successfully.")

def rsvp_prompt_view(request, token):
    rsvp_token = get_object_or_404(RSVPToken, token=token)

    if rsvp_token.responded:
        return render(request, "already_responded.html")

    if request.method == "POST":
        response = request.POST.get("response")
        if response in ["Yes", "No"]:
            rsvp_token.response = response
            rsvp_token.responded = True
            rsvp_token.save()

            student_profile = rsvp_token.user.student_profile
            student_profile.rsvp = (response == 'Yes')
            student_profile.rsvp_date = datetime.now(dt_timezone.utc) 
            student_profile.save()

            return render(request, "thank_you.html", {"response": response})

    return render(request, "rsvp_prompt.html", {"token": rsvp_token})

class ReunionDateView(APIView):
    def get(self, request, user_id):
        try:
            student = StudentProfile.objects.get(studentId=user_id)
        except StudentProfile.DoesNotExist:
            return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        reunion_date = student.reunion_date
        if not reunion_date:
            return Response({"error": "Reunion date not available."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "student_id": user_id,
            "reunion_date": reunion_date.isoformat()  # Convert datetime to string here
        })

class TimeUntilReunionView(APIView):
    def get(self, request, student_id):
        try:
            student = StudentProfile.objects.get(studentId=student_id)
            time_left = student.time_until_reunion()

            if time_left and time_left.total_seconds() > 0:
                total_seconds = time_left.total_seconds()
                minutes_left = total_seconds // 60
                approx_years_left = time_left.days // 365
                approx_months_left = (time_left.days % 365) // 30

                return Response({
                    "student_id": student_id,
                    "reunion_date": student.reunion_date().isoformat(),
                    "days_left": time_left.days,
                    "minutes_left": int(minutes_left),
                    "seconds_left": int(total_seconds),
                    "approx_years_left": int(approx_years_left),
                    "approx_months_left": int(approx_months_left)
                })

            else:
                return Response({
                    "student_id": student_id,
                    "message": "Reunion date has already passed or graduation year not set."
                }, status=status.HTTP_400_BAD_REQUEST)

        except StudentProfile.DoesNotExist:
            return Response({
                "error": "Student not found."
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return Response({
                "error": "Internal server error"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
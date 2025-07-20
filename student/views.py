from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import RSVPToken

from rest_framework.response import Response
from rest_framework import status
from core.models import StudentProfile

import os
from django.views.decorators.csrf import csrf_exempt
from django.core.management import call_command
from django.http import HttpResponse, HttpResponseForbidden

SECRET_TOKEN = os.getenv("RSVP_SECRET_TOKEN")

@csrf_exempt
def run_rsvp_reminders(request):
    token = request.GET.get('token')
    if token != SECRET_TOKEN:
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
            student_profile.rsvp_date = timezone.now()
            student_profile.save()

            return render(request, "thank_you.html", {"response": response})

    return render(request, "rsvp_prompt.html", {"token": rsvp_token})

def reunion_date_view(request, user_id):
    try:
        student = StudentProfile.objects.get(user_id=user_id)
    except StudentProfile.DoesNotExist:
        return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

    reunion_date = student.reunion_date  # Uses your property method
    if not reunion_date:
        return Response({"error": "Reunion date not available."}, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        "user_id": user_id,
        "reunion_date": reunion_date
    })
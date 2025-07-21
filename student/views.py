from django.shortcuts import render, get_object_or_404
from datetime import datetime, timezone as dt_timezone
from .models import RSVPToken
from django.http import JsonResponse, Http404

from django.utils.decorators import method_decorator
import json

from rest_framework.response import Response
from rest_framework import status
from core.models import StudentProfile, StudentShare, StudentLike

import logging

import os
from django.views.decorators.csrf import csrf_exempt
from django.core.management import call_command
from django.http import HttpResponse, HttpResponseForbidden
from rest_framework.views import APIView
from django.contrib.auth.decorators import login_required

from django.conf import settings

logger = logging.getLogger(__name__)

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
        logger.debug(f"Received request for user_id={user_id}")

        try:
            student = StudentProfile.objects.get(studentId=user_id)
            logger.debug("StudentProfile found")
            user_email = getattr(student.user, 'email', 'N/A') if hasattr(student, 'user') else 'No user'
            logger.debug(f"studentId={student.studentId}, user_email={user_email}")
        except StudentProfile.DoesNotExist:
            logger.warning(f"Student not found with studentId={user_id}")
            return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        reunion_date = student.reunion_date()
        logger.debug(f"Reunion date: {reunion_date}")

        if not reunion_date:
            logger.warning(f"Reunion date not available for studentId={user_id}")
            return Response({"error": "Reunion date not available."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "student_id": user_id,
            "reunion_date": reunion_date.isoformat()
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

""" Make sure user is authenticated before accessing this view. """

def get_shareable_student_profile(request, studentId):
    try:
        student = StudentProfile.objects.select_related('user').get(studentId=studentId, status='approved')
    except StudentProfile.DoesNotExist:
        raise Http404("Student profile not found or not approved.")

    data = {
        "full_name": student.user.full_name,
        "nickname": student.nickname,
        "quote": student.quote,
        "bio": student.bio,
        "best_memory": student.best_memory,
        "department": student.department,
        "graduation_year": student.graduation_year,
        "image_url": student.image.url if student.image else None,
        "share_url": f"https://frontenddomain.com/students/{student.studentId}"
    }
    return JsonResponse(data)

""" Frontend POSTs to /api/student/share/log/ with JSON data { studentId, platform } to log the share. """
""" Since I am not rendering the page, the frontend dev should ensure the user is authenticated before making this request. """

@method_decorator(csrf_exempt, name='dispatch')
def log_share(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            studentId = data.get('studentId')
            platform = data.get('platform')
            user = request.user  # Assuming user is authenticated
            
            student = StudentProfile.objects.get(studentId=studentId)
            StudentShare.objects.create(student=student, user=user, platform=platform)
            
            return JsonResponse({'message': 'Share logged'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid method'}, status=405)

""" Make sure user is authenticated before accessing this view. """
""" @login_required decorator can be used to enforce this. """

def toggle_like(request, student_id):
    student = get_object_or_404(StudentProfile, studentId=student_id)

    like, created = StudentLike.objects.get_or_create(
        student=student,
        user=request.user
    )

    if not created:
        # already liked, so unlike
        like.delete()
        liked = False
    else:
        liked = True

    return JsonResponse({
        'liked': liked,
        'total_likes': student.likes.count()
    })
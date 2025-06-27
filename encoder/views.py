from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from core.models import User, StudentProfile
from django.db import transaction
from rest_framework.permissions import IsAuthenticated

# Create your views here.
class CreateStudentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != 'encoder':
            return Response({'detail': 'Only encoders can create students'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    email=data['email'],
                    password=data['password'],
                    role='student',
                    full_name=data['full_name'],
                )
                StudentProfile.objects.create(
                    user=user,
                    image=data.get('image'),
                    course_program=data['course_program'],
                    graduation_year=data['graduation_year'],
                    bio=data.get('bio', ''),
                    created_by=request.user,
                    status='pending'
                )
            return Response({'detail': 'Student created and pending approval'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
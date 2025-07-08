from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import LoginSerializer
from django.http import JsonResponse, Http404
from core.models import EncoderProfile, StudentProfile

class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = authenticate(request, email=email, password=password)
        if user is None:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)

        user_data = {
            'email': user.email,
            'role': user.role,
            'full_name': user.full_name,
        }

        # Add extra info by role
        if user.role == 'encoder' and hasattr(user, 'encoder_profile'):
            profile = user.encoder_profile
            user_data.update({
                'encoder_type': profile.encoder_type,
                'university': profile.university,
                'department': profile.department,
                'encoderId': getattr(profile, 'encoderId', None),
            })

        elif user.role == 'student' and hasattr(user, 'student_profile'):
            profile = user.student_profile
            user_data.update({
                'course_program': profile.course_program,
                'graduation_year': profile.graduation_year,
                'studentId': getattr(profile, 'studentId', None),  
            })

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': user_data,
        })

class ListUsersView(APIView):
    def get(self, request):
        User = get_user_model()
        return Response([{"email": u.email} for u in User.objects.all()])

def encoders_by_campus(request, university_name):
    encoders = EncoderProfile.objects.filter(university=university_name).select_related('user')
    data = []
    for encoder in encoders:
        data.append({
            'encoderId': encoder.encoderId,          
            'email': encoder.user.email,
            'full_name': encoder.user.full_name,
            'phone_number': encoder.phone_number,
            'department': encoder.department,
            'encoder_type': encoder.get_encoder_type_display(),
        })
    return JsonResponse({'encoders': data})

def students_by_encoder(request, encoderId):
    try:
        encoder_profile = EncoderProfile.objects.get(encoderId=encoderId)
    except EncoderProfile.DoesNotExist:
        raise Http404("Encoder not found")

    students = StudentProfile.objects.filter(created_by=encoder_profile.user).select_related('user')
    data = []
    for student in students:

        image_url = request.build_absolute_uri(student.image.url) if student.image else None

        data.append({
            'studentId': student.studentId,
            'email': student.user.email,
            'full_name': student.user.full_name,
            'department': student.department,
            'university': student.university,
            'graduation_year': student.graduation_year,
            'quote': student.quote,
            'best_memory': student.best_memory,
            'bio': student.bio,
            'nickname': student.nickname,
            'future_goal': student.future_goal,
            'image': image_url,
        })
    return JsonResponse({'students': data})
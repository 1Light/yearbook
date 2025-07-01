from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import LoginSerializer

class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        print(email)
        print(password)

        user = authenticate(request, email=email, password=password)
        print(user)
        if user is None:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)

        user_data = {
            'email': user.email,
            'role': user.role,
            'full_name': user.full_name,
        }

        # add extra info by role
        if user.role == 'encoder' and hasattr(user, 'encoder_profile'):
            profile = user.encoder_profile
            user_data.update({
                'encoder_type': profile.encoder_type,
                'university': profile.university,
                'department': profile.department,
            })

        elif user.role == 'student' and hasattr(user, 'student_profile'):
            profile = user.student_profile
            user_data.update({
                'course_program': profile.course_program,
                'graduation_year': profile.graduation_year,
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
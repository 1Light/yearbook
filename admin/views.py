# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import get_user_model
from core.models import AdminProfile

User = get_user_model()

class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'superadmin'

class CreateAdminView(APIView):
    permission_classes = [IsSuperAdmin]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        full_name = request.data.get('full_name')
        institution_type = request.data.get('institution_type')
        institution_name = request.data.get('institution_name')

        if not all([email, password, full_name, institution_type, institution_name]):
            return Response({'error': 'Missing required fields.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.create_admin(
                email=email,
                password=password,
                institution_type=institution_type,
                institution_name=institution_name,
                full_name=full_name,
                created_by=request.user
            )
            AdminProfile.objects.create(
                user=user,
                institution_type=institution_type,
                institution_name=institution_name,
                created_by=request.user
            )
            return Response({'message': 'Admin created successfully.'}, status=status.HTTP_201_CREATED)

        except ValueError as ve:
            return Response({'error': str(ve)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': 'Something went wrong.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
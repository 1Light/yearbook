from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from core.models import User, EncoderProfile
from django.db import transaction
from rest_framework.permissions import IsAuthenticated

# Create your views here.
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view

User = get_user_model()

@api_view(['POST'])
def create_super_user(request):
    if request.data.get("secret") != "MY_SECRET_TOKEN":
        return Response({"error": "Unauthorized"}, status=401)

    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response({"error": "Missing fields"}, status=400)

    if User.objects.filter(email=email).exists():
        return Response({"error": "User already exists"}, status=400)

    user = User.objects.create_superuser(email=email, password=password)
    return Response({"success": f"Superuser {user.email} created"})

class CreateEncoderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != 'superadmin':
            return Response({'detail': 'Only superadmins can create encoders'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        try:
            with transaction.atomic():
                user = User.objects.create_encoder(
                    email=data['email'],
                    password=data['password'],
                    full_name=data['full_name'],
                )
                EncoderProfile.objects.create(
                    user=user,
                    phone_number=data['phone_number'],
                    university=data['university'],
                    department=data['department'],
                    encoder_type=data['encoder_type'],
                    additional_notes=data.get('additional_notes', ''),
                    created_by=request.user
                )
            return Response({'detail': 'Encoder created successfully'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
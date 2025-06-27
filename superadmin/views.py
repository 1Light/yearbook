from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from core.models import User, EncoderProfile
from django.db import transaction
from rest_framework.permissions import IsAuthenticated

# Create your views here.
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
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, permissions
from core.models import User, StudentProfile
from encoder.models import EventVideo
from django.db import transaction
from rest_framework.permissions import IsAuthenticated

import logging
logger = logging.getLogger(__name__)

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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_event(request):
    logger.debug("Received request to create event.")
    user = request.user
    logger.debug(f"Authenticated user: {user}")

    # Check if the user has an encoder profile of type "Videos and Images"
    try:
        encoder_profile = user.encoder_profile
        logger.debug(f"Found encoder profile: {encoder_profile}")
        logger.debug(f"Encoder type: {encoder_profile.encoder_type}")

        if encoder_profile.encoder_type != 3:  # 3 = 'Videos and Images'
            logger.warning("Unauthorized encoder type.")
            return Response({'error': 'You are not authorized to create video events.'},
                            status=status.HTTP_403_FORBIDDEN)
    except ObjectDoesNotExist:
        logger.error("Encoder profile not found.")
        return Response({'error': 'Encoder profile not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.exception("Unexpected error when fetching encoder profile.")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Get data from request
    title = request.data.get('title')
    link = request.data.get('link')
    description = request.data.get('description', '')
    tags = request.data.get('tags')

    logger.debug(f"Request data - Title: {title}, Link: {link}, Description: {description}, Tags: {tags}")

    if not title or not link:
        logger.warning("Missing title or link.")
        return Response({'error': 'Title and link are required fields.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        event = EventVideo.objects.create(
            encoder=encoder_profile,
            title=title,
            link=link,
            description=description
        )
        logger.debug(f"Created EventVideo: {event}")

        if tags:
            tag_list = [t.strip() for t in tags.split(',')]
            logger.debug(f"Parsed tags: {tag_list}")
            event.tags.add(*tag_list)

        return Response({'message': 'Event video created successfully.', 'event_id': event.event_id},
                        status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.exception("Failed to create event video.")
        return Response({'error': 'Internal server error while creating event.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
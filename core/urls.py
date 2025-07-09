from django.urls import path, include
from .views import LoginAPIView, ListUsersView, encoders_by_campus, students_by_encoder, check_storage

urlpatterns = [
    path('login', LoginAPIView.as_view(), name='login'),
    path("debug-users/", ListUsersView.as_view()),
    path('encoders/campus/<str:university_name>/', encoders_by_campus, name='encoders_by_campus'),
    path('debug/check-storage/', check_storage, name='check_storage'),
    path('encoders/<str:encoderId>/students/', students_by_encoder, name='students_by_encoder'),
]
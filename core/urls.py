from django.urls import path, include
from .views import LoginAPIView, ListUsersView

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='login'),
    path("debug-users/", ListUsersView.as_view()),
]
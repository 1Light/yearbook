# urls.py
from django.urls import path
from .views import CreateStudentView, create_event

urlpatterns = [
    path('create-student/', CreateStudentView.as_view(), name='create-student'),
    path('create-event/', create_event, name='create_event'),
]
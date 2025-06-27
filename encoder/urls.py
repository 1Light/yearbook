# urls.py
from django.urls import path
from .views import CreateStudentView

urlpatterns = [
    path('create-student/', CreateStudentView.as_view(), name='create-student'),
]
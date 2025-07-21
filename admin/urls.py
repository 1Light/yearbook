# urls.py
from django.urls import path
from .views import CreateAdminView

urlpatterns = [
    path('create-admin/', CreateAdminView.as_view(), name='create-admin'),
]
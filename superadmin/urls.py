# urls.py
from django.urls import path
from .views import CreateEncoderView

urlpatterns = [
    path('create-encoder/', CreateEncoderView.as_view(), name='create-encoder'),
]

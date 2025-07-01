# urls.py
from django.urls import path
from .views import CreateEncoderView, create_super_user

urlpatterns = [
    path('create-encoder/', CreateEncoderView.as_view(), name='create-encoder'),
    path('createsuper/', create_super_user, name='create-super-user'),
]

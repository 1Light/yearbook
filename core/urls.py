from django.urls import path, include
from .views import LoginAPIView

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='login'),

    path('encoder/', include('encoder.urls')),
    path('superadmin/', include('superadmin.urls')),
]
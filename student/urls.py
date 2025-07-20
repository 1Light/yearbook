# reunion/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("rsvp/<uuid:token>/", views.rsvp_prompt_view, name="rsvp_prompt"),
    path('run_rsvp_reminders/', views.run_rsvp_reminders, name='run_rsvp_reminders'),
    path('<int:user_id>/reunion-date/', views.reunion_date_view, name='reunion_date'),
]
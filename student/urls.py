# reunion/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("rsvp/<uuid:token>/", views.rsvp_prompt_view, name="rsvp_prompt"),
    path('run_rsvp_reminders/', views.run_rsvp_reminders, name='run_rsvp_reminders'),
    path('<str:user_id>/reunion-date/', views.ReunionDateView.as_view(), name='reunion_date'),
    path('<str:student_id>/time-until-reunion/', views.TimeUntilReunionView.as_view(), name='time_until_reunion'),
    path('<str:studentId>/share/', views.get_shareable_student_profile, name='student-share'),
    path('share/log/', views.log_share, name='log-share'),
    path('<str:student_id>/toggle-like/', views.toggle_like, name='toggle-like'),
    path('rsvp-students/', views.RSVPStudentListView.as_view(), name='rsvp-students'),
]
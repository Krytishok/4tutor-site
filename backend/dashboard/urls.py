from django.urls import path
from .views import TutorDashboardView, StudentDashboardView

urlpatterns = [
    path('tutor/', TutorDashboardView.as_view(), name='tutor-dashboard'),
    path('student/', StudentDashboardView.as_view(), name='student-dashboard'),
]

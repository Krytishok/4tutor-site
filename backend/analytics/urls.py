from django.urls import path
from .views import TutorAnalyticsView, StudentAnalyticsView

urlpatterns = [
    path('tutor/', TutorAnalyticsView.as_view(), name='tutor-analytics'),
    path('student/', StudentAnalyticsView.as_view(), name='student-analytics'),
]

from django.urls import path
from .views import (
    RegisterView, UserProfileView, TutorInvitationCreateView,
    StudentInvitationActionView, TutorStudentListView, LessonListCreateView, LessonRetrieveUpdateDestroyView)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('users/me/', UserProfileView.as_view(), name='user_profile'),

    # Приглашения
    path('tutor-students/invite/', TutorInvitationCreateView.as_view(), name='invite-student'),
    path('tutor-students/<int:pk>/action/', StudentInvitationActionView.as_view(), name='student-action'),
    path('tutor-students/', TutorStudentListView.as_view(), name='tutor-student-list'),

    # Уроки
    path('lessons/', LessonListCreateView.as_view(), name='lesson-list-create'),
    path('lessons/<int:pk>/', LessonRetrieveUpdateDestroyView.as_view(), name='lesson-detail'),
]
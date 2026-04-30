from django.urls import path
from . import views

urlpatterns = [
    path('', views.AssignmentListCreateView.as_view(), name='assignment-list'),
    path('<int:pk>/', views.AssignmentDetailView.as_view(), name='assignment-detail'),
    path('<int:pk>/upload-file/', views.AssignmentFileUploadView.as_view(), name='assignment-upload-file'),
    path('student-assignments/', views.StudentAssignmentListView.as_view(), name='student-assignment-list'),
    path('student-assignments/<int:pk>/', views.StudentAssignmentDetailView.as_view(), name='student-assignment-detail'),
    path('student-assignments/<int:pk>/upload/', views.SubmissionFileUploadView.as_view(), name='submission-upload'),
    path('<int:pk>/assign-students/', views.AssignmentAssignStudentsView.as_view(), name='assign-students')
]
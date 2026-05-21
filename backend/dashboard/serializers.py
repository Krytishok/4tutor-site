from django.utils import timezone
from django.contrib.auth import get_user_model
from django.utils.dateparse import parse_datetime
from rest_framework import serializers
from .models import Assignment, AssignmentFile, StudentAssignment, SubmissionFile
from api.models import TutorStudent


class DashboardSerializer(serializers.Serializer):
    students_number = serializers.IntegerField()
    active_assignments = serializers.IntegerField()
    overdue_assignments = serializers.IntegerField()
    next_lesson = serializers.DateField()
    
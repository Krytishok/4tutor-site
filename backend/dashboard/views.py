from rest_framework import generics, status, parsers
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
from api.permissions import IsTutor

from .serializers import DashboardSerializer



class DashboardInfo(generics.ListAPIView):
    serializer_class = DashboardSerializer
    permission_classes = [IsTutor]

    def get_queryset(self):
        return super().get_queryset()

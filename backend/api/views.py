from rest_framework import generics, status
from datetime import datetime
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils.dateparse import parse_date, parse_datetime
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied
from .permissions import IsTutor, IsStudent
from .serializers import (
    UserRegistrationSerializer, UserSerializer,
    LessonCreateSerializer, TutorInvitationSerializer, InvitationActionSerializer, TutorStudentListSerializer, LessonDetailSerializer, LessonUpdateSerializer
)
from .models import User, Lesson, TutorStudent, InvitationStatus


class RegisterView(generics.CreateAPIView):
    """Регистрация нового пользователя"""
    queryset = get_user_model().objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"message": "User registered successfully", "user_id": user.id},
            status=status.HTTP_201_CREATED
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Получение и редактирование профиля текущего пользователя"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class TutorInvitationCreateView(generics.CreateAPIView):
    serializer_class = TutorInvitationSerializer
    permission_classes = [IsAuthenticated, IsTutor]

class StudentInvitationActionView(generics.UpdateAPIView):
    serializer_class = InvitationActionSerializer
    permission_classes = [IsAuthenticated, IsStudent]
    http_method_names = ['patch']  # Разрешаем только PATCH

    def get_queryset(self):
        # Ученик видит только свои ожидающие приглашения
        return TutorStudent.objects.filter(student=self.request.user, status=InvitationStatus.PENDING)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': instance.status}, status=status.HTTP_200_OK)

class TutorStudentListView(generics.ListAPIView):
    serializer_class = TutorStudentListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = TutorStudent.objects.select_related('tutor', 'student')
        status_filter = self.request.query_params.get('status')

        allowed_statuses = {
            InvitationStatus.PENDING,
            InvitationStatus.ACTIVE,
            InvitationStatus.REJECTED,
            InvitationStatus.CANCELLED,
        }
        if status_filter and status_filter not in allowed_statuses:
            raise PermissionDenied('Недопустимое значение фильтра status.')

        if user.role == User.Role.TUTOR:
            qs = qs.filter(tutor=user)
        else:
            qs = qs.filter(student=user)

        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs.order_by('-created_at')


class StudentPendingInvitationsListView(generics.ListAPIView):
    serializer_class = TutorStudentListSerializer
    permission_classes = [IsAuthenticated, IsStudent]

    def get_queryset(self):
        return TutorStudent.objects.select_related('tutor', 'student').filter(
            student=self.request.user,
            status=InvitationStatus.PENDING
        ).order_by('-created_at')


def _parse_dt_or_date_to_aware(value: str, *, end_of_day: bool = False):
    dt_value = parse_datetime(value)
    if dt_value is not None:
        return timezone.make_aware(dt_value) if timezone.is_naive(dt_value) else dt_value

    date_value = parse_date(value)
    if date_value is None:
        return None

    hour, minute, second, microsecond = (23, 59, 59, 999999) if end_of_day else (0, 0, 0, 0)
    combined = datetime(
        year=date_value.year,
        month=date_value.month,
        day=date_value.day,
        hour=hour,
        minute=minute,
        second=second,
        microsecond=microsecond,
    )
    return timezone.make_aware(combined)

class LessonListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return LessonCreateSerializer if self.request.method == 'POST' else LessonDetailSerializer

    def get_queryset(self):
        user = self.request.user
        # Предзагрузка связей для предотвращения N+1
        qs = Lesson.objects.select_related('tutor').prefetch_related('students')
        if user.role == User.Role.TUTOR:
            qs = qs.filter(tutor=user)
        else:
            qs = qs.filter(students=user)

        from_param = self.request.query_params.get('from')
        to_param = self.request.query_params.get('to')
        weekdays_only = self.request.query_params.get('weekdays_only') == 'true'

        if from_param:
            from_dt = _parse_dt_or_date_to_aware(from_param, end_of_day=False)
            if from_dt is None:
                raise PermissionDenied('Некорректный параметр from.')
            qs = qs.filter(start_time__gte=from_dt)

        if to_param:
            to_dt = _parse_dt_or_date_to_aware(to_param, end_of_day=True)
            if to_dt is None:
                raise PermissionDenied('Некорректный параметр to.')
            qs = qs.filter(start_time__lte=to_dt)

        if weekdays_only:
            qs = qs.filter(start_time__week_day__in=[2, 3, 4, 5, 6])

        return qs.order_by('-start_time')

    def create(self, request, *args, **kwargs):
        if request.user.role != User.Role.TUTOR:
            raise PermissionDenied('Только репетиторы могут создавать уроки.')
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(tutor=self.request.user)

    def create(self, request, *args, **kwargs):
        if request.user.role != User.Role.TUTOR:
            raise PermissionDenied('Только репетиторы могут создавать уроки.')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lesson = serializer.save(tutor=request.user)
        response_serializer = LessonDetailSerializer(lesson, context=self.get_serializer_context())
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return LessonUpdateSerializer
        return LessonDetailSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Lesson.objects.select_related('tutor').prefetch_related('students')
        if user.role == User.Role.TUTOR:
            return qs.filter(tutor=user)
        return qs.filter(students=user)

    def update(self, request, *args, **kwargs):
        lesson = self.get_object()
        if request.user.role != User.Role.TUTOR or lesson.tutor_id != request.user.id:
            raise PermissionDenied('Только репетитор-владелец может менять урок.')
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        lesson = self.get_object()
        if request.user.role != User.Role.TUTOR or lesson.tutor_id != request.user.id:
            raise PermissionDenied('Только репетитор-владелец может удалить урок.')
        return super().destroy(request, *args, **kwargs)
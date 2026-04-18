from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.exceptions import PermissionDenied
from .permissions import IsTutor, IsStudent
from .serializers import (
    UserRegistrationSerializer, UserSerializer,
    LessonCreateSerializer, TutorInvitationSerializer, InvitationActionSerializer, TutorStudentListSerializer, LessonDetailSerializer
)
from .models import User, Lesson, TutorStudent


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
        return TutorStudent.objects.filter(student=self.request.user, status='pending')

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
        if user.role == User.Role.TUTOR:
            return qs.filter(tutor=user).order_by('-created_at')
        return qs.filter(student=user).order_by('-created_at')

class LessonListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return LessonCreateSerializer if self.request.method == 'POST' else LessonDetailSerializer

    def get_queryset(self):
        user = self.request.user
        # Предзагрузка связей для предотвращения N+1
        qs = Lesson.objects.select_related('tutor').prefetch_related('students')
        if user.role == User.Role.TUTOR:
            return qs.filter(tutor=user).order_by('-start_time')
        return qs.filter(students=user).order_by('-start_time')

    def create(self, request, *args, **kwargs):
        if request.user.role != User.Role.TUTOR:
            raise PermissionDenied('Только репетиторы могут создавать уроки.')
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(tutor=self.request.user)

class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LessonDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Lesson.objects.select_related('tutor').prefetch_related('students')
        if user.role == User.Role.TUTOR:
            return qs.filter(tutor=user)
        return qs.filter(students=user)
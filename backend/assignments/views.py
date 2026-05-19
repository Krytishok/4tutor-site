from rest_framework import generics, status, parsers
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q

from transliterate import translit

from .models import Assignment, StudentAssignment, SubmissionFile, AssignmentFile
from .serializers import (
    AssignStudentsSerializer,
    AssignmentCreateUpdateSerializer,
    AssignmentDetailSerializer,
    AssignmentFileSerializer,
    AssignmentListSerializer,
    StudentAssignmentDetailSerializer,
    StudentAssignmentListSerializer,
    SubmissionFileSerializer,
    GradeAndCommentSerializer,
)
from .permissions import IsAssignmentTutorOrReadOnly, IsStudentAssignmentRecipient, IsTutor, IsStudent

class AssignmentListCreateView(generics.ListCreateAPIView):
    """
    GET: список заданий с фильтрацией и пагинацией.
    POST: создать задание (только репетитор).
    """
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]  # для загрузки файлов
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AssignmentCreateUpdateSerializer
        return AssignmentListSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsTutor()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        queryset = Assignment.objects.all()
        
        if user.role == 'tutor':
            queryset = queryset.filter(tutor=user)
        else:
            # Ученик видит задания, назначенные ему
            queryset = queryset.filter(
                student_assignments__student=user
            ).distinct()
        
        # Фильтрация по предмету
        subject = self.request.query_params.get('subject')
        if subject:
            queryset = queryset.filter(subject__icontains=subject)
        
        # Фильтрация по названию
        title = self.request.query_params.get('title')
        if title:
            queryset = queryset.filter(title__icontains=title)
        
        # Фильтрация по дедлайну (для учеников)
        deadline_before = self.request.query_params.get('deadline_before')
        deadline_after = self.request.query_params.get('deadline_after')
        if user.role == 'student':
            if deadline_before:
                queryset = queryset.filter(
                    student_assignments__student=user,
                    student_assignments__deadline__lte=deadline_before
                ).distinct()
            if deadline_after:
                queryset = queryset.filter(
                    student_assignments__student=user,
                    student_assignments__deadline__gte=deadline_after
                ).distinct()
        
        # Сортировка
        ordering = self.request.query_params.get('ordering', '-created_at')
        valid_orderings = ['created_at', '-created_at', 'title', '-title', 'subject', '-subject']
        if ordering in valid_orderings:
            queryset = queryset.order_by(ordering)
        
        return queryset.prefetch_related('files')

    def perform_create(self, serializer):
        serializer.save(tutor=self.request.user)


class AssignmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Детали задания. Обновлять/удалять может только репетитор-владелец."""
    permission_classes = [IsAuthenticated, IsAssignmentTutorOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return AssignmentCreateUpdateSerializer
        return AssignmentDetailSerializer

    def get_queryset(self):
        return Assignment.objects.prefetch_related('files', 'student_assignments__student')
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        # Возвращаем полный детальный объект
        detail_serializer = AssignmentDetailSerializer(instance, context={'request': request})
        return Response(detail_serializer.data)


class StudentAssignmentListView(generics.ListAPIView):
    """Список назначений для текущего пользователя с фильтрацией и пагинацией."""
    serializer_class = StudentAssignmentListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = StudentAssignment.objects.all().select_related('student', 'assignment')
        
        if user.role == 'tutor':
            queryset = queryset.filter(assignment__tutor=user)
        else:
            queryset = queryset.filter(student=user)
        
        # Фильтрация по предмету (через связанное задание)
        subject = self.request.query_params.get('subject')
        if subject:
            queryset = queryset.filter(assignment__subject__icontains=subject)
        
        # Фильтрация по названию задания
        title = self.request.query_params.get('title')
        if title:
            queryset = queryset.filter(assignment__title__icontains=title)
        
        # Фильтрация по статусу
        status = self.request.query_params.get('status')
        if status and status in ['assigned', 'submitted', 'graded']:
            queryset = queryset.filter(status=status)
        
        # Фильтрация по дедлайну
        deadline_before = self.request.query_params.get('deadline_before')
        deadline_after = self.request.query_params.get('deadline_after')
        if deadline_before:
            queryset = queryset.filter(deadline__lte=deadline_before)
        if deadline_after:
            queryset = queryset.filter(deadline__gte=deadline_after)
        
        # Сортировка
        ordering = self.request.query_params.get('ordering', 'deadline')
        valid_orderings = ['deadline', '-deadline', 'status', '-status', 'assignment__title', '-assignment__title']
        if ordering in valid_orderings:
            queryset = queryset.order_by(ordering)
        
        return queryset

class StudentAssignmentDetailView(generics.RetrieveUpdateAPIView):
    """Детали конкретного назначения.
    Ученик может загрузить файлы и сдать работу.
    Репетитор может выставить оценку.
    """
    permission_classes = [IsAuthenticated, IsStudentAssignmentRecipient]
    queryset = StudentAssignment.objects.all()

    def get_serializer_class(self):
        if self.request.method in ('PATCH', 'PUT'):
            # Если репетитор ставит оценку - используем GradeAndCommentSerializer
            if self.request.user.role == 'tutor':
                return GradeAndCommentSerializer
            # Иначе ученик может загружать файлы ответа, но это делается через отдельный эндпоинт
        return StudentAssignmentDetailSerializer

    def check_object_permissions(self, request, obj):
        # Только ученик, которому назначено, или репетитор-владелец задания могут видеть/менять
        if request.user.role == 'student':
            if obj.student != request.user:
                raise PermissionDenied('Вы не можете просматривать это назначение.')
        elif request.user.role == 'tutor':
            if obj.assignment.tutor != request.user:
                raise PermissionDenied('Вы не являетесь репетитором этого задания.')
        else:
            raise PermissionDenied('Недостаточно прав.')

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        # Ученик сдаёт работу (меняет статус на submitted)
        if request.user.role == 'student' and 'submit' in request.data:
            try:
                instance.submit()
                return Response({'status': instance.status})
            except ValidationError as e:
                return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Репетитор выставляет оценку
        if request.user.role == 'tutor':
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            # При выставлении оценки статус меняем на GRADED
            serializer.validated_data['status'] = StudentAssignment.Status.GRADED
            serializer.save()
            return Response(serializer.data)

        return Response({'detail': 'Недопустимое действие'}, status=status.HTTP_400_BAD_REQUEST)


class SubmissionFileUploadView(generics.CreateAPIView):
    """Загрузка файла ответа учеником."""
    serializer_class = SubmissionFileSerializer
    permission_classes = [IsAuthenticated, IsStudent]
    parser_classes = [parsers.MultiPartParser]

    def perform_create(self, serializer):
        # Получаем назначение по pk в URL
        student_assignment = get_object_or_404(
            StudentAssignment,
            pk=self.kwargs['pk'],
            student=self.request.user,
            status=StudentAssignment.Status.ASSIGNED
        )
        if not student_assignment.can_submit():
            raise PermissionDenied('Срок сдачи истёк или работа уже сдана.')
        serializer.save(student_assignment=student_assignment)

class AssignmentFileUploadView(generics.CreateAPIView):
    """Загрузка дополнительного файла к заданию репетитором."""
    serializer_class = AssignmentFileSerializer
    permission_classes = [IsAuthenticated, IsTutor]
    parser_classes = [parsers.MultiPartParser]

    def perform_create(self, serializer):
        assignment = get_object_or_404(Assignment, pk=self.kwargs['pk'], tutor=self.request.user)
        serializer.save(assignment=assignment)


# assignments/views.py

class AssignmentAssignStudentsView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsTutor]
    serializer_class = AssignStudentsSerializer

    def create(self, request, *args, **kwargs):
        # Получаем задание и проверяем, что оно принадлежит репетитору
        assignment = get_object_or_404(
            Assignment,
            pk=self.kwargs['pk'],
            tutor=request.user
        )

        # Валидация входных данных
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assignments_data = serializer.validated_data['assignments_data']

        assigned = []
        skipped_student_ids = []

        # Создаём назначения, пропуская уже существующие
        for item in assignments_data:
            student_id = item['student_id']
            deadline = item['deadline']

            if StudentAssignment.objects.filter(
                assignment=assignment,
                student_id=student_id
            ).exists():
                skipped_student_ids.append(student_id)
                continue

            student_assignment = StudentAssignment.objects.create(
                assignment=assignment,
                student_id=student_id,
                deadline=deadline
            )
            assigned.append(student_assignment)

        # Сериализуем созданные назначения для ответа
        output_serializer = StudentAssignmentListSerializer(
            assigned,
            many=True
        )

        return Response(
            {
                'assigned': output_serializer.data,
                'assigned_count': len(assigned),
                'skipped_student_ids': skipped_student_ids,
                'skipped_count': len(skipped_student_ids),
            },
            status=status.HTTP_201_CREATED
        )
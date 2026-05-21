from rest_framework import generics, status, parsers
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count, Avg
from api.permissions import IsTutor, IsStudent

from .serializers import (
    TutorDashboardSerializer,
    StudentDashboardSerializer,
)
from assignments.models import Assignment, StudentAssignment
from api.models import TutorStudent, User


class TutorDashboardView(APIView):
    """
    Дашборд репетитора.
    Возвращает всю необходимую информацию в одном запросе.
    """
    permission_classes = [IsAuthenticated, IsTutor]

    def get(self, request):
        user = request.user
        
        # Блок 1: Ближайшие дедлайны (3-5 ближайших активных назначений)
        upcoming_deadlines = StudentAssignment.objects.filter(
            assignment__tutor=user,
            status__in=['assigned', 'submitted']
        ).select_related('student', 'assignment').order_by('deadline')[:5]
        
        # Блок 2: Статистика по заданиям
        total_assignments = Assignment.objects.filter(tutor=user).count()
        active_assignments = StudentAssignment.objects.filter(
            assignment__tutor=user,
            status__in=['assigned', 'submitted']
        ).count()
        submitted_pending = StudentAssignment.objects.filter(
            assignment__tutor=user,
            status='submitted'
        ).count()
        graded_count = StudentAssignment.objects.filter(
            assignment__tutor=user,
            status='graded'
        ).count()
        
        assignment_stats = {
            'total_assignments': total_assignments,
            'active_assignments': active_assignments,
            'submitted_pending': submitted_pending,
            'graded_count': graded_count,
        }
        
        # Блок 3: Последние созданные задания (3-5 последних)
        recent_assignments = Assignment.objects.filter(
            tutor=user
        ).annotate(
            students_count=Count('student_assignments')
        ).order_by('-created_at')[:5]
        
        # Блок 4: Активные ученики (со статусом active из TutorStudentRelation)
        active_student_relations = TutorStudent.objects.filter(
            tutor=user,
            status='active'
        ).select_related('student')
        
        active_students = []
        for relation in active_student_relations[:10]:
            student = relation.student
            pending_count = StudentAssignment.objects.filter(
                student=student,
                status='assigned'
            ).count()
            active_students.append({
                'id': student.id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'email': student.email,
                'pending_assignments_count': pending_count,
            })
        
        # Блок 5: Требуют внимания
        # Назначения со статусом submitted (сдано, но не оценено)
        submitted_pending_qs = StudentAssignment.objects.filter(
            assignment__tutor=user,
            status='submitted'
        ).select_related('student', 'assignment')[:5]
        
        # Просроченные дедлайны (deadline < now и статус assigned)
        overdue_qs = StudentAssignment.objects.filter(
            assignment__tutor=user,
            deadline__lt=timezone.now(),
            status='assigned'
        ).select_related('student', 'assignment')[:5]
        
        needs_attention = {
            'submitted_pending_count': submitted_pending_qs.count(),
            'submitted_pending': [
                {
                    'id': sa.id,
                    'assignment_title': sa.assignment.title,
                    'student_name': sa.student.get_full_name(),
                    'deadline': sa.deadline,
                    'status': sa.status,
                    'submitted_at': sa.submitted_at,
                }
                for sa in submitted_pending_qs
            ],
            'overdue_count': overdue_qs.count(),
            'overdue': [
                {
                    'id': sa.id,
                    'assignment_title': sa.assignment.title,
                    'student_name': sa.student.get_full_name(),
                    'deadline': sa.deadline,
                    'status': sa.status,
                    'submitted_at': sa.submitted_at,
                }
                for sa in overdue_qs
            ],
        }
        
        data = {
            'upcoming_deadlines': [
                {
                    'id': sa.id,
                    'assignment_title': sa.assignment.title,
                    'student_name': sa.student.get_full_name(),
                    'deadline': sa.deadline,
                    'status': sa.status,
                }
                for sa in upcoming_deadlines
            ],
            'assignment_stats': assignment_stats,
            'recent_assignments': [
                {
                    'id': a.id,
                    'title': a.title,
                    'subject': a.subject,
                    'created_at': a.created_at,
                    'students_count': a.students_count,
                }
                for a in recent_assignments
            ],
            'active_students': active_students,
            'needs_attention': needs_attention,
        }
        
        serializer = TutorDashboardSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        
        return Response(serializer.data)


class StudentDashboardView(APIView):
    """
    Дашборд ученика.
    Возвращает всю необходимую информацию в одном запросе.
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        user = request.user
        
        # Блок 1: Активные задания (3-5 ближайших по дедлайну назначений со статусом assigned)
        active_assignments = StudentAssignment.objects.filter(
            student=user,
            status='assigned'
        ).select_related('assignment__tutor').order_by('deadline')[:5]
        
        # Блок 2: Ожидают оценки (заданя со статусом submitted)
        pending_grades = StudentAssignment.objects.filter(
            student=user,
            status='submitted'
        ).order_by('-submitted_at')[:5]
        
        # Блок 3: Последние оценки (3 последних оценённых задания со статусом graded)
        recent_grades = StudentAssignment.objects.filter(
            student=user,
            status='graded'
        ).select_related('assignment').order_by('-submitted_at')[:3]
        
        # Блок 4: Статистика
        total_assignments = StudentAssignment.objects.filter(student=user).count()
        completed_count = StudentAssignment.objects.filter(
            student=user,
            status__in=['submitted', 'graded']
        ).count()
        
        # Средний балл (только для оценённых работ)
        avg_grade_result = StudentAssignment.objects.filter(
            student=user,
            status='graded',
            grade__isnull=False
        ).aggregate(avg_grade=Avg('grade'))
        average_grade = avg_grade_result['avg_grade'] or 0.0
        
        # Прогресс по выполненным заданиям
        progress_percentage = (completed_count / total_assignments * 100) if total_assignments > 0 else 0.0
        
        stats = {
            'total_assignments': total_assignments,
            'completed_count': completed_count,
            'average_grade': round(average_grade, 2),
            'progress_percentage': round(progress_percentage, 2),
        }
        
        # Блок 5: Мои репетиторы (те, кто назначил хотя бы одно задание)
        tutors_data = StudentAssignment.objects.filter(
            student=user
        ).values('assignment__tutor', 'assignment__tutor__first_name', 'assignment__tutor__last_name').annotate(
            assignments_count=Count('id')
        ).order_by('-assignments_count')[:10]
        
        my_tutors = [
            {
                'tutor_id': item['assignment__tutor'],
                'tutor_name': f"{item['assignment__tutor__first_name']} {item['assignment__tutor__last_name']}",
                'assignments_count': item['assignments_count'],
            }
            for item in tutors_data
        ]
        
        data = {
            'active_assignments': [
                {
                    'id': sa.id,
                    'assignment_title': sa.assignment.title,
                    'tutor_name': sa.assignment.tutor.get_full_name(),
                    'subject': sa.assignment.subject,
                    'deadline': sa.deadline,
                }
                for sa in active_assignments
            ],
            'pending_grades': [
                {
                    'id': sa.id,
                    'assignment_title': sa.assignment.title,
                    'submitted_at': sa.submitted_at,
                    'status': sa.status,
                }
                for sa in pending_grades
            ],
            'recent_grades': [
                {
                    'id': sa.id,
                    'assignment_title': sa.assignment.title,
                    'grade': sa.grade,
                    'tutor_comment': sa.tutor_comment,
                    'submitted_at': sa.submitted_at,
                }
                for sa in recent_grades
            ],
            'stats': stats,
            'my_tutors': my_tutors,
        }
        
        serializer = StudentDashboardSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        
        return Response(serializer.data)

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Q, Count, Avg
from api.permissions import IsTutor, IsStudent

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
        upcoming_deadlines_qs = StudentAssignment.objects.filter(
            assignment__tutor=user,
            status__in=['assigned', 'submitted']
        ).select_related('student', 'assignment').order_by('deadline')[:5]

        upcoming_deadlines = [
            {
                'id': sa.id,
                'assignment_title': sa.assignment.title,
                'student_name': sa.student.get_full_name(),
                'deadline': sa.deadline.isoformat() if sa.deadline else None,
                'status': sa.status,
            }
            for sa in upcoming_deadlines_qs
        ]

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
        recent_assignments_qs = Assignment.objects.filter(
            tutor=user
        ).annotate(
            students_count=Count('student_assignments')
        ).order_by('-created_at')[:5]

        recent_assignments = [
            {
                'id': a.id,
                'title': a.title,
                'subject': a.subject or '',
                'created_at': a.created_at.isoformat() if a.created_at else None,
                'students_count': a.students_count,
            }
            for a in recent_assignments_qs
        ]

        # Блок 4: Активные ученики (со статусом active из TutorStudentRelation)
        active_student_relations = TutorStudent.objects.filter(
            tutor=user,
            status='active'
        ).select_related('student')[:10]

        active_students = []
        for relation in active_student_relations:
            student = relation.student
            pending_count = StudentAssignment.objects.filter(
                student=student,
                status='assigned'
            ).count()
            active_students.append({
                'id': student.id,
                'first_name': student.first_name or '',
                'last_name': student.last_name or '',
                'email': student.email or '',
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
                    'deadline': sa.deadline.isoformat() if sa.deadline else None,
                    'status': sa.status,
                    'submitted_at': sa.submitted_at.isoformat() if sa.submitted_at else None,
                }
                for sa in submitted_pending_qs
            ],
            'overdue_count': overdue_qs.count(),
            'overdue': [
                {
                    'id': sa.id,
                    'assignment_title': sa.assignment.title,
                    'student_name': sa.student.get_full_name(),
                    'deadline': sa.deadline.isoformat() if sa.deadline else None,
                    'status': sa.status,
                    'submitted_at': sa.submitted_at.isoformat() if sa.submitted_at else None,
                }
                for sa in overdue_qs
            ],
        }

        data = {
            'upcoming_deadlines': upcoming_deadlines,
            'assignment_stats': assignment_stats,
            'recent_assignments': recent_assignments,
            'active_students': active_students,
            'needs_attention': needs_attention,
        }

        return Response(data)


class StudentDashboardView(APIView):
    """
    Дашборд ученика.
    Возвращает всю необходимую информацию в одном запросе.
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        user = request.user

        # Блок 1: Активные задания (3-5 ближайших по дедлайну назначений со статусом assigned)
        active_assignments_qs = StudentAssignment.objects.filter(
            student=user,
            status='assigned'
        ).select_related('assignment__tutor').order_by('deadline')[:5]

        active_assignments = [
            {
                'id': sa.id,
                'assignment_title': sa.assignment.title,
                'tutor_name': sa.assignment.tutor.get_full_name(),
                'subject': sa.assignment.subject or '',
                'deadline': sa.deadline.isoformat() if sa.deadline else None,
            }
            for sa in active_assignments_qs
        ]

        # Блок 2: Ожидают оценки (заданя со статусом submitted)
        pending_grades_qs = StudentAssignment.objects.filter(
            student=user,
            status='submitted'
        ).order_by('-submitted_at')[:5]

        pending_grades = [
            {
                'id': sa.id,
                'assignment_title': sa.assignment.title,
                'submitted_at': sa.submitted_at.isoformat() if sa.submitted_at else None,
                'status': sa.status,
            }
            for sa in pending_grades_qs
        ]

        # Блок 3: Последние оценки (3 последних оценённых задания со статусом graded)
        recent_grades_qs = StudentAssignment.objects.filter(
            student=user,
            status='graded'
        ).select_related('assignment').order_by('-submitted_at')[:3]

        recent_grades = [
            {
                'id': sa.id,
                'assignment_title': sa.assignment.title,
                'grade': sa.grade,
                'tutor_comment': sa.tutor_comment or '',
                'submitted_at': sa.submitted_at.isoformat() if sa.submitted_at else None,
            }
            for sa in recent_grades_qs
        ]

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
                'tutor_name': f"{item['assignment__tutor__first_name'] or ''} {item['assignment__tutor__last_name'] or ''}".strip(),
                'assignments_count': item['assignments_count'],
            }
            for item in tutors_data if item['assignment__tutor']
        ]

        data = {
            'active_assignments': active_assignments,
            'pending_grades': pending_grades,
            'recent_grades': recent_grades,
            'stats': stats,
            'my_tutors': my_tutors,
        }

        return Response(data)
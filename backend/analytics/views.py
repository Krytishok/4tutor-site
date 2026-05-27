from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db.models import Q, Count, Avg, F, Window
from django.db.models.functions import TruncMonth, Lag
from api.permissions import IsTutor, IsStudent

from assignments.models import Assignment, StudentAssignment
from api.models import TutorStudent, User


class TutorAnalyticsView(APIView):
    """
    Аналитика для репетитора.
    Возвращает данные для графиков и сводки по ученикам.
    """
    permission_classes = [IsAuthenticated, IsTutor]

    def get(self, request):
        user = request.user

        # Блок 1: Средний балл по месяцам (для графика)
        monthly_avg_grade = StudentAssignment.objects.filter(
            assignment__tutor=user,
            status='graded',
            grade__isnull=False
        ).annotate(
            month=TruncMonth('submitted_at')
        ).values('month').annotate(
            avg_grade=Avg('grade')
        ).order_by('month')

        average_grades_chart = [
            {
                'month': item['month'].strftime('%Y-%m'),
                'avg_grade': round(item['avg_grade'], 2) if item['avg_grade'] else 0
            }
            for item in monthly_avg_grade
        ]

        # Блок 2: Статусы выполнения заданий (для круговой диаграммы)
        total_assigned = StudentAssignment.objects.filter(
            assignment__tutor=user
        ).count()
        
        status_counts = StudentAssignment.objects.filter(
            assignment__tutor=user
        ).values('status').annotate(
            count=Count('id')
        )

        assignment_completion = {
            'total': total_assigned,
            'assigned': 0,
            'submitted': 0,
            'graded': 0
        }
        for item in status_counts:
            status_key = item['status']
            if status_key in assignment_completion:
                assignment_completion[status_key] = item['count']

        # Блок 3: Сводка по ученикам
        students_data = TutorStudent.objects.filter(
            tutor=user
        ).select_related('student').annotate(
            total_assignments=Count('student__student_assignments', filter=Q(student__student_assignments__assignment__tutor=user)),
            completed_assignments=Count('student__student_assignments', filter=Q(student__student_assignments__assignment__tutor=user, student__student_assignments__status__in=['submitted', 'graded'])),
            avg_grade=Avg('student__student_assignments__grade', filter=Q(student__student_assignments__assignment__tutor=user, student__student_assignments__status='graded', student__student_assignments__grade__isnull=False))
        )

        students_summary = []
        for relation in students_data:
            student = relation.student
            
            # Расчет процента выполнения
            completion_percentage = 0
            if relation.total_assignments > 0:
                completion_percentage = round(relation.completed_assignments / relation.total_assignments * 100, 1)
            
            # Определение прогресса (статуса динамики)
            progress_status = self._calculate_progress_status(student, user)
            
            students_summary.append({
                'id': student.id,
                'first_name': student.first_name or '',
                'last_name': student.last_name or '',
                'email': student.email or '',
                'average_grade': round(relation.avg_grade, 2) if relation.avg_grade else None,
                'completion_percentage': completion_percentage,
                'progress_status': progress_status,
                'total_assignments': relation.total_assignments,
                'completed_assignments': relation.completed_assignments,
            })

        data = {
            'average_grades_chart': average_grades_chart,
            'assignment_completion': assignment_completion,
            'students_summary': students_summary,
        }

        return Response(data)

    def _calculate_progress_status(self, student, tutor):
        """
        Вычисляет статус прогресса ученика на основе последних оценок.
        Возвращает: 'growing', 'falling', 'stable', 'no_change'
        """
        graded_assignments = StudentAssignment.objects.filter(
            student=student,
            assignment__tutor=tutor,
            status='graded',
            grade__isnull=False
        ).order_by('-submitted_at')[:5]

        if len(graded_assignments) < 2:
            return 'no_change'

        grades = [sa.grade for sa in graded_assignments if sa.grade is not None]
        
        if len(grades) < 2:
            return 'no_change'

        # Сравниваем среднее последних 3 оценок с предыдущими
        recent_avg = sum(grades[:3]) / len(grades[:3]) if len(grades) >= 3 else sum(grades[:2]) / 2
        previous_avg = sum(grades[3:]) / len(grades[3:]) if len(grades) > 3 else grades[-1] if len(grades) > 2 else grades[0]

        diff = recent_avg - previous_avg

        if diff > 0.5:
            return 'growing'
        elif diff < -0.5:
            return 'falling'
        elif abs(diff) <= 0.5:
            return 'stable'
        else:
            return 'no_change'


class StudentAnalyticsView(APIView):
    """
    Аналитика для ученика (личная статистика).
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        user = request.user

        # Средний балл по месяцам
        monthly_avg_grade = StudentAssignment.objects.filter(
            student=user,
            status='graded',
            grade__isnull=False
        ).annotate(
            month=TruncMonth('submitted_at')
        ).values('month').annotate(
            avg_grade=Avg('grade')
        ).order_by('month')

        average_grades_chart = [
            {
                'month': item['month'].strftime('%Y-%m'),
                'avg_grade': round(item['avg_grade'], 2) if item['avg_grade'] else 0
            }
            for item in monthly_avg_grade
        ]

        # Статусы выполнения
        total_assigned = StudentAssignment.objects.filter(
            student=user
        ).count()
        
        status_counts = StudentAssignment.objects.filter(
            student=user
        ).values('status').annotate(
            count=Count('id')
        )

        assignment_completion = {
            'total': total_assigned,
            'assigned': 0,
            'submitted': 0,
            'graded': 0
        }
        for item in status_counts:
            status_key = item['status']
            if status_key in assignment_completion:
                assignment_completion[status_key] = item['count']

        # Общая статистика
        overall_stats = {
            'total_assignments': total_assigned,
            'average_grade': 0,
            'completion_percentage': 0
        }

        if total_assigned > 0:
            completed = StudentAssignment.objects.filter(
                student=user,
                status__in=['submitted', 'graded']
            ).count()
            overall_stats['completion_percentage'] = round(completed / total_assigned * 100, 1)

            avg_result = StudentAssignment.objects.filter(
                student=user,
                status='graded',
                grade__isnull=False
            ).aggregate(avg=Avg('grade'))
            overall_stats['average_grade'] = round(avg_result['avg'], 2) if avg_result['avg'] else 0

        data = {
            'average_grades_chart': average_grades_chart,
            'assignment_completion': assignment_completion,
            'overall_stats': overall_stats,
        }

        return Response(data)

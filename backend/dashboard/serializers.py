from django.utils import timezone
from django.contrib.auth import get_user_model
from django.utils.dateparse import parse_datetime
from rest_framework import serializers
from assignments.models import Assignment, AssignmentFile, StudentAssignment, SubmissionFile
from api.models import TutorStudent, User


UserModel = get_user_model()



class TutorDeadlineItemSerializer(serializers.ModelSerializer):
    """Сериализатор для элемента списка ближайших дедлайнов"""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)
    
    class Meta:
        model = StudentAssignment
        fields = ['id', 'assignment_title', 'student_name', 'deadline', 'status']


class TutorAssignmentStatsSerializer(serializers.Serializer):
    """Статистика по заданиям для репетитора"""
    total_assignments = serializers.IntegerField()
    active_assignments = serializers.IntegerField()
    submitted_pending = serializers.IntegerField()
    graded_count = serializers.IntegerField()


class TutorRecentAssignmentSerializer(serializers.ModelSerializer):
    """Сериализатор для последних созданных заданий"""
    students_count = serializers.IntegerField(source='student_assignments.count', read_only=True)
    
    class Meta:
        model = Assignment
        fields = ['id', 'title', 'subject', 'created_at', 'students_count']


class TutorActiveStudentSerializer(serializers.ModelSerializer):
    """Сериализатор для активных учеников"""
    pending_assignments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'pending_assignments_count']
    
    def get_pending_assignments_count(self, obj):
        # Количество назначенных, но не сданных заданий
        return StudentAssignment.objects.filter(
            student=obj,
            status__in=['assigned']
        ).count()


class TutorAttentionItemSerializer(serializers.ModelSerializer):
    """Элемент списка требующих внимания"""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)
    
    class Meta:
        model = StudentAssignment
        fields = ['id', 'assignment_title', 'student_name', 'deadline', 'status', 'submitted_at']


class TutorDashboardSerializer(serializers.Serializer):
    """Основной сериализатор дашборда репетитора"""
    # Блок 1: Ближайшие дедлайны
    upcoming_deadlines = TutorDeadlineItemSerializer(many=True)
    
    # Блок 2: Статистика по заданиям
    assignment_stats = TutorAssignmentStatsSerializer()
    
    # Блок 3: Последние созданные задания
    recent_assignments = TutorRecentAssignmentSerializer(many=True)
    
    # Блок 4: Активные ученики
    active_students = TutorActiveStudentSerializer(many=True)
    
    # Блок 5: Требуют внимания
    needs_attention = serializers.SerializerMethodField()
    
    def get_needs_attention(self, obj):
        request = self.context.get('request')
        if not request:
            return {'submitted_pending': [], 'overdue': []}
        
        user = request.user
        
        # Назначения со статусом submitted (сдано, но не оценено)
        submitted_pending = StudentAssignment.objects.filter(
            assignment__tutor=user,
            status='submitted'
        ).select_related('student', 'assignment')[:5]
        
        # Просроченные дедлайны (deadline < now и статус assigned)
        overdue = StudentAssignment.objects.filter(
            assignment__tutor=user,
            deadline__lt=timezone.now(),
            status='assigned'
        ).select_related('student', 'assignment')[:5]
        
        return {
            'submitted_pending_count': submitted_pending.count(),
            'submitted_pending': TutorAttentionItemSerializer(submitted_pending, many=True).data,
            'overdue_count': overdue.count(),
            'overdue': TutorAttentionItemSerializer(overdue, many=True).data,
        }


# ==================== STUDENT DASHBOARD SERIALIZERS ====================

class StudentActiveAssignmentSerializer(serializers.ModelSerializer):
    """Активные задания для ученика"""
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)
    tutor_name = serializers.CharField(source='assignment.tutor.get_full_name', read_only=True)
    subject = serializers.CharField(source='assignment.subject', read_only=True)
    
    class Meta:
        model = StudentAssignment
        fields = ['id', 'assignment_title', 'tutor_name', 'subject', 'deadline']


class StudentPendingGradeSerializer(serializers.ModelSerializer):
    """Задания, ожидающие оценки"""
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)
    
    class Meta:
        model = StudentAssignment
        fields = ['id', 'assignment_title', 'submitted_at', 'status']


class StudentRecentGradeSerializer(serializers.ModelSerializer):
    """Последние оценённые задания"""
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)
    grade_display = serializers.CharField(source='grade', read_only=True)
    
    class Meta:
        model = StudentAssignment
        fields = ['id', 'assignment_title', 'grade', 'tutor_comment', 'submitted_at']


class StudentStatsSerializer(serializers.Serializer):
    """Статистика для ученика"""
    total_assignments = serializers.IntegerField()
    completed_count = serializers.IntegerField()
    average_grade = serializers.FloatField()
    progress_percentage = serializers.FloatField()


class StudentTutorItemSerializer(serializers.Serializer):
    """Элемент списка репетиторов"""
    tutor_id = serializers.IntegerField()
    tutor_name = serializers.CharField()
    assignments_count = serializers.IntegerField()


class StudentDashboardSerializer(serializers.Serializer):
    """Основной сериализатор дашборда ученика"""
    # Блок 1: Активные задания
    active_assignments = StudentActiveAssignmentSerializer(many=True)
    
    # Блок 2: Ожидают оценки
    pending_grades = StudentPendingGradeSerializer(many=True)
    
    # Блок 3: Последние оценки
    recent_grades = StudentRecentGradeSerializer(many=True)
    
    # Блок 4: Статистика
    stats = StudentStatsSerializer()
    
    # Блок 5: Мои репетиторы
    my_tutors = StudentTutorItemSerializer(many=True)
    
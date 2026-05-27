from rest_framework import serializers
from api.models import User


class AverageGradesChartSerializer(serializers.Serializer):
    """Сериализатор для графика среднего балла по месяцам"""
    month = serializers.CharField()
    avg_grade = serializers.FloatField()


class AssignmentCompletionSerializer(serializers.Serializer):
    """Сериализатор для статистики выполнения заданий"""
    total = serializers.IntegerField()
    assigned = serializers.IntegerField()
    submitted = serializers.IntegerField()
    graded = serializers.IntegerField()


class StudentSummaryItemSerializer(serializers.Serializer):
    """Сериализатор для элемента сводки по ученику"""
    id = serializers.IntegerField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.CharField()
    average_grade = serializers.FloatField(allow_null=True)
    completion_percentage = serializers.FloatField()
    progress_status = serializers.CharField()
    total_assignments = serializers.IntegerField()
    completed_assignments = serializers.IntegerField()


class TutorAnalyticsSerializer(serializers.Serializer):
    """Основной сериализатор аналитики для репетитора"""
    average_grades_chart = AverageGradesChartSerializer(many=True)
    assignment_completion = AssignmentCompletionSerializer()
    students_summary = StudentSummaryItemSerializer(many=True)


class OverallStatsSerializer(serializers.Serializer):
    """Сериализатор общей статистики для ученика"""
    total_assignments = serializers.IntegerField()
    average_grade = serializers.FloatField()
    completion_percentage = serializers.FloatField()


class StudentAnalyticsSerializer(serializers.Serializer):
    """Основной сериализатор аналитики для ученика"""
    average_grades_chart = AverageGradesChartSerializer(many=True)
    assignment_completion = AssignmentCompletionSerializer()
    overall_stats = OverallStatsSerializer()

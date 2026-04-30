from datetime import timezone

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from rest_framework import serializers
from .models import Assignment, AssignmentFile, StudentAssignment, SubmissionFile
from api.models import TutorStudent

User = get_user_model()

class UserBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name')


class AssignmentFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentFile
        fields = ('id', 'file', 'uploaded_at')
        read_only_fields = ('uploaded_at',)


class AssignmentListSerializer(serializers.ModelSerializer):
    """Краткое представление задания в списке"""
    tutor = UserBriefSerializer(read_only=True)
    files_count = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = ('id', 'tutor', 'title', 'subject', 'created_at', 'files_count')

    def get_files_count(self, obj):
        return obj.files.count()


class AssignmentDetailSerializer(serializers.ModelSerializer):
    """Детальное представление задания с файлами и назначениями"""
    tutor = UserBriefSerializer(read_only=True)
    files = AssignmentFileSerializer(many=True, read_only=True)
    student_assignments = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = ('id', 'tutor', 'title', 'description', 'subject',
                  'created_at', 'updated_at', 'files', 'student_assignments')

    def get_student_assignments(self, obj):
        # Возвращаем все назначения, но в зависимости от роли можно фильтровать
        request = self.context.get('request')
        qs = obj.student_assignments.select_related('student')
        if request and request.user.role == 'student':
            qs = qs.filter(student=request.user)
        return StudentAssignmentListSerializer(qs, many=True, context=self.context).data


class AssignmentCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/редактирования задания репетитором.
    Позволяет сразу загрузить файлы и назначить учеников с дедлайнами.
    """
    files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False,
        help_text='Список файлов для прикрепления'
    )
    students = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text='Список ID учеников для назначения'
    )
    deadline = serializers.DateTimeField(
        write_only=True,
        required=False,
        help_text='Общий дедлайн для всех указанных учеников'
    )
    # Можно сделать индивидуальные дедлайны через отдельный эндпоинт

    class Meta:
        model = Assignment
        fields = ('title', 'description', 'subject', 'files', 'students', 'deadline')

    def validate_students(self, value):
        tutor = self.context['request'].user
        # Проверяем, что все ученики привязаны к репетитору
        valid_ids = set(
            TutorStudent.objects.filter(tutor=tutor, status='active')
            .values_list('student_id', flat=True)
        )
        invalid = [uid for uid in value if uid not in valid_ids]
        if invalid:
            raise serializers.ValidationError(
                f'Ученики с ID {invalid} не привязаны к вам или связь не активна.'
            )
        return value

    def validate_deadline(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError('Дедлайн должен быть в будущем.')
        return value

    def create(self, validated_data):
        files_data = validated_data.pop('files', [])
        students_ids = validated_data.pop('students', [])
        deadline = validated_data.pop('deadline', None)

        # Создаём задание
        assignment = Assignment.objects.create(**validated_data)

        # Сохраняем файлы
        for f in files_data:
            AssignmentFile.objects.create(assignment=assignment, file=f)

        # Назначаем ученикам
        for student_id in students_ids:
            try:
                StudentAssignment.objects.create(
                    assignment=assignment,
                    student_id=student_id,
                    deadline=deadline
                )
            except IntegrityError:
                # Пара уже существует – игнорируем или можно выдать предупреждение
                pass

        return assignment

    def update(self, instance, validated_data):
        # Обновление основных полей
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.subject = validated_data.get('subject', instance.subject)
        instance.save()

        # Обработка новых файлов: просто добавляем, старые не трогаем
        files_data = validated_data.pop('files', [])
        for f in files_data:
            AssignmentFile.objects.create(assignment=instance, file=f)
        return instance


class StudentAssignmentListSerializer(serializers.ModelSerializer):
    student = UserBriefSerializer(read_only=True)
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)

    class Meta:
        model = StudentAssignment
        fields = ('id', 'assignment', 'assignment_title', 'student',
                  'deadline', 'status', 'grade', 'submitted_at')


class StudentAssignmentDetailSerializer(serializers.ModelSerializer):
    student = UserBriefSerializer(read_only=True)
    assignment = AssignmentListSerializer(read_only=True)
    submission_files = serializers.SerializerMethodField()

    class Meta:
        model = StudentAssignment
        fields = '__all__'
        read_only_fields = ('assignment', 'student', 'submitted_at')

    def get_submission_files(self, obj):
        files = obj.submission_files.all()
        return SubmissionFileSerializer(files, many=True).data


class SubmissionFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionFile
        fields = ('id', 'file', 'uploaded_at')
        read_only_fields = ('uploaded_at',)


class GradeAndCommentSerializer(serializers.ModelSerializer):
    """Используется репетитором для выставления оценки и комментария"""
    class Meta:
        model = StudentAssignment
        fields = ('grade', 'tutor_comment', 'status')
        extra_kwargs = {'status': {'read_only': True}}



class AssignStudentsSerializer(serializers.Serializer):
    assignments_data = serializers.ListField(
        child=serializers.JSONField(),
        write_only=True,
        help_text='Список объектов {"student_id": int, "deadline": "datetime"}'
    )

    def validate_assignments_data(self, value):
        if not value:
            raise serializers.ValidationError('Список назначений не может быть пустым.')
        validated = []
        student_ids = []
        for item in value:
            if not isinstance(item, dict):
                raise serializers.ValidationError('Каждый элемент должен быть JSON-объектом.')
            student_id = item.get('student_id')
            deadline = item.get('deadline')
            if not student_id:
                raise serializers.ValidationError('student_id обязателен.')
            if not deadline:
                raise serializers.ValidationError('deadline обязателен.')
            student_ids.append(student_id)
            validated.append({'student_id': student_id, 'deadline': deadline})
        # Проверяем, что все ученики привязаны к текущему репетитору
        from .models import TutorStudent  # импорт здесь или в начале файла
        tutor = self.context['request'].user
        active_student_ids = set(
            TutorStudent.objects.filter(
                tutor=tutor,
                status='active'
            ).values_list('student_id', flat=True)
        )
        missing = [sid for sid in student_ids if sid not in active_student_ids]
        if missing:
            raise serializers.ValidationError(
                f'Ученики с ID {missing} не привязаны к вам или связь не активна.'
            )
        return validated
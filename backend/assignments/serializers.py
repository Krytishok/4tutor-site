from django.utils import timezone
from django.contrib.auth import get_user_model
from django.utils.dateparse import parse_datetime
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
    files = AssignmentFileSerializer(many=True, read_only=True)

    class Meta:
        model = Assignment
        fields = ('id', 'tutor', 'title', 'subject', 'description', 'created_at', 'files_count', 'files')

    def get_files_count(self, obj):
        return obj.files.count()


class AssignmentDetailSerializer(serializers.ModelSerializer):
    """Детальное представление задания с файлами и назначениями"""
    tutor = UserBriefSerializer(read_only=True)
    files = AssignmentFileSerializer(many=True, read_only=True)
    student_assignments = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = ('id', 'tutor', 'title', 'description', 'subject', 'max_grade',
                  'created_at', 'updated_at', 'files', 'student_assignments')

    def get_student_assignments(self, obj):
        # Возвращаем все назначения, но в зависимости от роли можно фильтровать
        request = self.context.get('request')
        qs = obj.student_assignments.select_related('student')
        if request and request.user.role == 'student':
            qs = qs.filter(student=request.user)
            return StudentAssignmentListSerializer(qs, many=True, context=self.context).data
        else:
            # Для репетитора — полный сериализатор с файлами и комментариями
            return StudentAssignmentDetailSerializer(qs, many=True, context=self.context).data
        



class AssignmentCreateUpdateSerializer(serializers.ModelSerializer):
    files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False,
    )
    students = serializers.JSONField(
        write_only=True,
        required=False,
        help_text='JSON-массив объектов {"student_id": int, "deadline": "ISO8601"}'
    )
    remove_file_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
    )
    max_grade = serializers.IntegerField(required=False, min_value=1, max_value=100)

    class Meta:
        model = Assignment
        fields = ('title', 'description', 'subject', 'max_grade',
                  'remove_file_ids', 'files', 'students')

    def validate_students(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError('Должен быть массив.')

        tutor = self.context['request'].user
        valid_student_ids = set(
            TutorStudent.objects.filter(tutor=tutor, status='active')
            .values_list('student_id', flat=True)
        )
        validated = []
        for item in value:
            if not isinstance(item, dict):
                raise serializers.ValidationError('Каждый элемент должен быть объектом.')
            student_id = item.get('student_id')
            deadline_str = item.get('deadline')
            if not student_id:
                raise serializers.ValidationError('student_id обязателен.')
            if not deadline_str:
                raise serializers.ValidationError('deadline обязателен.')
            if student_id not in valid_student_ids:
                raise serializers.ValidationError(
                    f'Ученик с ID {student_id} не привязан к вам или связь не активна.'
                )

            # Парсим deadline
            deadline = parse_datetime(deadline_str)
            if not deadline:
                raise serializers.ValidationError(f'Некорректный формат даты: {deadline_str}')
            if deadline <= timezone.now():
                raise serializers.ValidationError('Дедлайн должен быть в будущем.')
            validated.append({'student_id': student_id, 'deadline': deadline})
        return validated

    def create(self, validated_data):
        files_data = validated_data.pop('files', [])
        students_data = validated_data.pop('students', [])

        assignment = Assignment.objects.create(**validated_data)

        for f in files_data:
            AssignmentFile.objects.create(assignment=assignment, file=f)

        for item in students_data:
            StudentAssignment.objects.create(
                assignment=assignment,
                student_id=item['student_id'],
                deadline=item['deadline']
            )
        return assignment

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.subject = validated_data.get('subject', instance.subject)
        instance.max_grade = validated_data.get('max_grade', instance.max_grade)
        instance.save()

        # Удаление файлов
        remove_file_ids = validated_data.pop('remove_file_ids', [])
        if remove_file_ids:
            AssignmentFile.objects.filter(assignment=instance, id__in=remove_file_ids).delete()

        # Добавление новых файлов
        files_data = validated_data.pop('files', [])
        for f in files_data:
            AssignmentFile.objects.create(assignment=instance, file=f)

        # Полная замена назначений
        if 'students' in validated_data:
            students_data = validated_data.pop('students')
            # удаляем старые назначения
            instance.student_assignments.all().delete()
            for item in students_data:
                StudentAssignment.objects.create(
                    assignment=instance,
                    student_id=item['student_id'],
                    deadline=item['deadline']
                )
        return instance

class StudentAssignmentListSerializer(serializers.ModelSerializer):
    student = UserBriefSerializer(read_only=True)
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)
    tutor = UserBriefSerializer(source='assignment.tutor', read_only=True) 

    class Meta:
        model = StudentAssignment
        fields = ('id', 'assignment', 'assignment_title', 'tutor', 'student',
                  'deadline', 'status', 'grade', 'submitted_at', 'student_comment')


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
        extra_kwargs = {
            'grade': {'required': False},
            'tutor_comment': {'required': False}
        }

    def validate_grade(self, value):
        max_grade = self.instance.assignment.max_grade
        if value > max_grade:
            raise serializers.ValidationError(f'Оценка не может быть больше {max_grade}.')
        return value


class StudentCommentSerializer(serializers.ModelSerializer):
    """Используется учеником для добавления комментария к заданию"""
    class Meta:
        model = StudentAssignment
        fields = ('student_comment',)
        extra_kwargs = {
            'student_comment': {'required': True}
        }



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
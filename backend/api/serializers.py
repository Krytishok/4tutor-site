from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import User, Lesson, TutorStudent


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'role', 'password')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'role': {'required': False}  # По умолчанию student в create_user
        }

    def create(self, validated_data):
        return User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password'],
            role=validated_data.get('role', User.Role.STUDENT)
        )


class UserSerializer(serializers.ModelSerializer):
    """Для просмотра и обновления профиля авторизованного пользователя"""
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined')
        read_only_fields = ('id', 'email', 'is_active', 'date_joined')


class UserBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name')

# 1️⃣ Создание приглашения (Tutor -> Student by email)
class TutorInvitationSerializer(serializers.ModelSerializer):
    student_email = serializers.EmailField(write_only=True)

    class Meta:
        model = TutorStudent
        fields = ('student_email', 'subject')

    def validate_student_email(self, email):
        if not User.objects.filter(email=email, role=User.Role.STUDENT, is_active=True).exists():
            raise serializers.ValidationError('Ученик не найден или не активен.')
        return email

    def create(self, validated_data):
        email = validated_data.pop('student_email')
        tutor = self.context['request'].user
        student = User.objects.get(email=email)

        relation, created = TutorStudent.objects.get_or_create(
            tutor=tutor,
            student=student,
            defaults={'subject': validated_data.get('subject'), 'status': 'pending'}
        )
        if not created:
            if relation.status == 'active':
                raise serializers.ValidationError({'student_email': 'Ученик уже в вашем списке.'})
            if relation.status == 'pending':
                raise serializers.ValidationError({'student_email': 'Приглашение уже отправлено.'})
            # Повторное приглашение после отказа
            relation.status = 'pending'
            if validated_data.get('subject'):
                relation.subject = validated_data['subject']
            relation.save()
        return relation

# 2️⃣ Подтверждение/Отклонение (Student action)
class InvitationActionSerializer(serializers.ModelSerializer):
    action = serializers.ChoiceField(choices=['accept', 'reject'], write_only=True)

    class Meta:
        model = TutorStudent
        fields = ('action',)

    def update(self, instance, validated_data):
        instance.status = 'active' if validated_data['action'] == 'accept' else 'rejected'
        instance.save()
        return instance

# 3️⃣ Список связей (Read-only)
class TutorStudentListSerializer(serializers.ModelSerializer):
    tutor = UserBriefSerializer(read_only=True)
    student = UserBriefSerializer(read_only=True)

    class Meta:
        model = TutorStudent
        fields = ('id', 'tutor', 'student', 'subject', 'status', 'created_at')

# 4️⃣ Создание урока (Tutor only)
class LessonCreateSerializer(serializers.ModelSerializer):
    students = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=User.Role.STUDENT),
        many=True
    )

    class Meta:
        model = Lesson
        fields = ('students', 'subject', 'start_time', 'end_time', 'meeting_url')

    def validate_students(self, students):
        tutor = self.context['request'].user
        # Разрешаем добавлять только активных учеников
        active_ids = set(
            TutorStudent.objects.filter(tutor=tutor, status='active')
            .values_list('student_id', flat=True)
        )
        invalid = [str(s.id) for s in students if s.id not in active_ids]
        if invalid:
            raise serializers.ValidationError(f'Ученики с ID {invalid} не привязаны к вам.')
        return students

# 5️⃣ Чтение урока (Detail/List)
class LessonDetailSerializer(serializers.ModelSerializer):
    tutor = UserBriefSerializer(read_only=True)
    students = UserBriefSerializer(many=True, read_only=True)

    class Meta:
        model = Lesson
        fields = '__all__'
        read_only_fields = ('id', 'tutor', 'created_at', 'updated_at')
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import serializers
from django.utils import timezone
from django.db.models import Q
from .models import User, Lesson, TutorStudent, InvitationStatus


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
            defaults={'subject': validated_data.get('subject'), 'status': InvitationStatus.PENDING}
        )
        if not created:
            if relation.status == 'active':
                raise serializers.ValidationError({'student_email': 'Ученик уже в вашем списке.'})
            if relation.status == 'pending':
                raise serializers.ValidationError({'student_email': 'Приглашение уже отправлено.'})
            # Повторное приглашение после отказа/отмены.
            relation.status = InvitationStatus.PENDING
            if validated_data.get('subject'):
                relation.subject = validated_data['subject']
            relation.save()
        tutor_name = tutor.get_full_name() or tutor.email
        send_mail(
            subject='Приглашение от репетитора',
            message=(
                f'Здравствуйте!\n\n'
                f'Репетитор {tutor_name} приглашает вас на занятия'
                f'{f" по предмету {relation.subject}" if relation.subject else ""}.\n'
                f'Войдите в систему и примите приглашение в разделе "Приглашения".'
            ),
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
            recipient_list=[student.email],
            fail_silently=True,
        )
        return relation

# Подтверждение/Отклонение (Student action)
class InvitationActionSerializer(serializers.ModelSerializer):
    action = serializers.ChoiceField(choices=['accept', 'reject', 'cancel'], write_only=True)

    class Meta:
        model = TutorStudent
        fields = ('action',)

    def update(self, instance, validated_data):
        action = validated_data['action']
        if action == 'accept':
            instance.status = 'active'
        elif action == 'reject':
            instance.status = 'rejected'
        else:
            instance.status = 'cancelled'
        instance.save()
        return instance

# Список связей (Read-only)
class TutorStudentListSerializer(serializers.ModelSerializer):
    tutor = UserBriefSerializer(read_only=True)
    student = UserBriefSerializer(read_only=True)

    class Meta:
        model = TutorStudent
        fields = ('id', 'tutor', 'student', 'subject', 'status', 'created_at')

#  Создание урока (Tutor only)
class LessonCreateSerializer(serializers.ModelSerializer):
    students = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=User.Role.STUDENT),
        many=True
    )

    class Meta:
        model = Lesson
        fields = ('students', 'subject', 'start_time', 'end_time', 'meeting_url', 'is_recurring_weekly')

    def validate(self, attrs):
        #Валидация времени
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')
        tutor = self.context['request'].user

        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError({'end_time': 'Время окончания должно быть позже времени начала.'})
        if start_time and timezone.is_naive(start_time):
            raise serializers.ValidationError({'start_time': 'Время начала должно содержать timezone.'})
        if end_time and timezone.is_naive(end_time):
            raise serializers.ValidationError({'end_time': 'Время окончания должно содержать timezone.'})
        

        # Проверка на пересечение уроков
        overlapping = Lesson.objects.filter(
            Q(start_time__lt=end_time) & Q(end_time__gt=start_time)
            )

        if self.instance:
            overlapping = overlapping.exclude(pk=self.instance.pk)
        if overlapping.exists():
            raise serializers.ValidationError('Это время пересекается с другим занятием.')




        
        return attrs

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


class LessonUpdateSerializer(LessonCreateSerializer):
    class Meta(LessonCreateSerializer.Meta):
        fields = ('students', 'subject', 'start_time', 'end_time', 'meeting_url', 'status', 'is_recurring_weekly')
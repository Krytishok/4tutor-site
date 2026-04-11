from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import User

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password]
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'role', 'password')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'role': {'required': False}
        }

    def create(self, validated_data):
        # Используем ваш кастомный менеджер для корректного хеширования пароля
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
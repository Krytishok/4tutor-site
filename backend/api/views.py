from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserRegistrationSerializer, UserSerializer
from django.contrib.auth import get_user_model

class RegisterView(generics.CreateAPIView):
    """Регистрация нового пользователя"""
    queryset = get_user_model().objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"message": "User registered successfully", "user_id": user.id},
            status=status.HTTP_201_CREATED
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Получение и редактирование профиля текущего пользователя"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
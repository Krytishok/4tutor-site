from rest_framework.permissions import BasePermission, SAFE_METHODS
from api.permissions import IsTutor, IsStudent

class IsAssignmentTutorOrReadOnly(BasePermission):
    """
    Разрешает изменение только репетитору-владельцу задания.
    Чтение доступно всем аутентифицированным пользователям.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.tutor == request.user

class IsStudentAssignmentRecipient(BasePermission):
    """
    Доступ к назначению: ученик видит только свои, репетитор – только в своих заданиях.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == 'student':
            return obj.student == user
        if user.role == 'tutor':
            return obj.assignment.tutor == user
        return False
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.html import format_html

from .models import User, Lesson, TutorStudent


# ================= USER ADMIN =================
class AddUserForm(forms.ModelForm):
    """Форма создания пользователя с подтверждением пароля"""
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'role')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UpdateUserForm(forms.ModelForm):
    """Форма редактирования пользователя (пароль хешируется отдельно)"""
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = (
            'email', 'password', 'first_name', 'last_name', 'role',
            'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'
        )

    def clean_password(self):
        return self.initial["password"]


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UpdateUserForm
    add_form = AddUserForm

    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff', 'date_joined')
    list_display_links = ('email',)
    list_filter = ('role', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    filter_horizontal = ('groups', 'user_permissions')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Персональные данные', {'fields': ('first_name', 'last_name', 'role')}),
        ('Доступ и права', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Системные даты', {'fields': ('last_login', 'date_joined'), 'classes': ('collapse',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )


# ================= LESSON ADMIN =================
@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'subject', 'tutor', 'get_students_display', 
        'start_time', 'end_time', 'status', 'meeting_url', 'created_at'
    )
    list_display_links = ('id', 'subject')
    list_filter = ('status', 'subject', 'tutor__role', 'start_time')
    search_fields = (
        'subject', 'tutor__email', 'tutor__first_name', 'tutor__last_name',
        'students__email', 'students__first_name', 'students__last_name'
    )
    ordering = ('-start_time',)
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('students',)  # Удобный виджет для M2M

    fieldsets = (
        ('Основная информация', {
            'fields': ('subject', 'tutor', 'students', 'status', 'meeting_url')
        }),
        ('Расписание', {
            'fields': ('start_time', 'end_time')
        }),
        ('Аудит', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_students_display(self, obj):
        """Возвращает имена учеников через запятую"""
        return ", ".join([f"{s.first_name} {s.last_name}" for s in obj.students.all()])
    get_students_display.short_description = 'Ученики'


# ================= TUTOR-STUDENT ADMIN =================
@admin.register(TutorStudent)
class TutorStudentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'get_tutor_full', 'get_student_full', 
        'subject', 'status', 'created_at'
    )
    list_display_links = ('id',)
    list_filter = ('status', 'subject', 'tutor', 'student')
    search_fields = (
        'tutor__email', 'tutor__first_name', 'tutor__last_name',
        'student__email', 'student__first_name', 'student__last_name',
        'subject'
    )
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

    fieldsets = (
        ('Связь', {'fields': ('tutor', 'student', 'subject', 'status')}),
        ('Метаданные', {'fields': ('created_at',), 'classes': ('collapse',)}),
    )

    def get_tutor_full(self, obj):
        return f"{obj.tutor.first_name} {obj.tutor.last_name} ({obj.tutor.email})"
    get_tutor_full.short_description = 'Репетитор'

    def get_student_full(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name} ({obj.student.email})"
    get_student_full.short_description = 'Ученик'
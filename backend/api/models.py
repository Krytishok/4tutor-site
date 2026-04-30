from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(
            self, email, first_name, last_name, password=None,
            role='student', commit=True):
        """
        Creates and saves a User with the given email, first name, last name
        and password.
        """
        if not email:
            raise ValueError(_('Users must have an email address'))
        if not first_name:
            raise ValueError(_('Users must have a first name'))
        if not last_name:
            raise ValueError(_('Users must have a last name'))

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            role=role,
        )

        user.set_password(password)
        if commit:
            user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password):
        """
        Creates and saves a superuser with the given email, first name,
        last name and password.
        """
        user = self.create_user(
            email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            commit=False,
            role="admin"
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    # Роли пользователей
    class Role(models.TextChoices):
        TUTOR = 'tutor', _('Репетитор')
        STUDENT = 'student', _('Ученик')
    
    email = models.EmailField(
        verbose_name=_('email address'), max_length=255, unique=True
    )
    # password field supplied by AbstractBaseUser
    # last_login field supplied by AbstractBaseUser
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    
    # Поле для роли пользователя
    role = models.CharField(
        _('role'),
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
        help_text=_('User role: tutor or student')
    )

    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'
        ),
    )
    # is_superuser field provided by PermissionsMixin
    # groups field provided by PermissionsMixin
    # user_permissions field provided by PermissionsMixin

    date_joined = models.DateTimeField(
        _('date joined'), default=timezone.now
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    @property
    def is_tutor(self):
        """Check if user is a tutor"""
        return self.role == self.Role.TUTOR
    
    @property
    def is_student(self):
        """Check if user is a student"""
        return self.role == self.Role.STUDENT

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def __str__(self):
        role_display = self.get_role_display()
        return '{} <{}> ({})'.format(self.get_full_name(), self.email, role_display)

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True
    

class LessonStatus(models.TextChoices):
    """Статусы уроков"""
    PLANNED = 'planned', _('Запланировано')
    IN_PROGRESS = 'in_progress', _('В процессе')
    COMPLETED = 'completed', _('Завершено')
    CANCELLED = 'cancelled', _('Отменено')

class Lesson(models.Model):
    tutor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='lessons_as_tutor',
        limit_choices_to={'role': User.Role.TUTOR}
    )
    students = models.ManyToManyField(
        User,
        related_name='lessons_as_student',
        limit_choices_to={'role': User.Role.STUDENT}
    )
    subject = models.CharField(_('предмет'), max_length=200)
    start_time = models.DateTimeField(_('время начала'))
    end_time = models.DateTimeField(_('время окончания'))
    
    status = models.CharField(
        _('статус'),
        max_length=20,
        choices=LessonStatus.choices,
        default=LessonStatus.PLANNED
    )
    meeting_url = models.URLField(
        _('ссылка на встречу'), 
        max_length=500, 
        blank=True, 
        null=True
    )
    is_recurring_weekly = models.BooleanField(
        _('еженедельное повторение'),
        default=False
    )
    created_at = models.DateTimeField(_('создан'), auto_now_add=True)
    updated_at = models.DateTimeField(_('обновлен'), auto_now=True)

    class Meta:
        verbose_name = _('урок')
        verbose_name_plural = _('уроки')
        ordering = ['-start_time']


class InvitationStatus(models.TextChoices):
    PENDING = 'pending', _('Ожидает')
    ACTIVE = 'active', _('Активна')
    REJECTED = 'rejected', _('Отклонена')
    CANCELLED = 'cancelled', _('Отменена')

class TutorStudent(models.Model):
    tutor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assigned_students',
        limit_choices_to={'role': User.Role.TUTOR}
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assigned_tutors',
        limit_choices_to={'role': User.Role.STUDENT}
    )
    subject = models.CharField(_('предмет'), max_length=200, blank=True, null=True)
    status = models.CharField(
        _('статус связи'),
        max_length=20,
        choices=InvitationStatus.choices,
        default=InvitationStatus.PENDING
    )
    created_at = models.DateTimeField(_('дата привязки'), auto_now_add=True)

    class Meta:
        verbose_name = _('связь репетитор-ученик')
        verbose_name_plural = _('связи репетитор-ученик')
        constraints = [
            models.UniqueConstraint(
                fields=['tutor', 'student'],
                name='unique_tutor_student_pair'
            )
        ]

    def clean(self):
        if self.tutor.role != User.Role.TUTOR:
            raise ValidationError({'tutor': _('Пользователь должен быть репетитором.')})
        if self.student.role != User.Role.STUDENT:
            raise ValidationError({'student': _('Пользователь должен быть учеником.')})
        super().clean()

    def __str__(self):
        return f"{self.tutor.get_full_name()} ↔ {self.student.get_full_name()}"






from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django.utils.text import get_valid_filename
from transliterate import translit

import os
import unicodedata

User = settings.AUTH_USER_MODEL

class Assignment(models.Model):
    """Задание, создаваемое репетитором"""
    tutor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        limit_choices_to={'role': 'tutor'},
        related_name='created_assignments',
        verbose_name='Репетитор'
    )
    title = models.CharField('Название', max_length=255)
    description = models.TextField('Описание', blank=True)
    subject = models.CharField('Предмет', max_length=200, blank=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)
    max_grade = models.PositiveSmallIntegerField('Максимальная оценка', blank=True, default=10)

    class Meta:
        verbose_name = 'Задание'
        verbose_name_plural = 'Задания'
        ordering = ['-created_at']

    def __str__(self):
        return f'[{self.subject}] {self.title}'


def sanitize_filename(filename):
    """Нормализует имя файла: сохраняет кириллицу, но убирает опасные символы"""
    # Нормализация Unicode (NFC)
    filename = unicodedata.normalize('NFC', filename)
    # Оставляем только безопасные символы
    name, ext = os.path.splitext(filename)
    # Заменяем пробелы и спецсимволы на подчёркивание, но сохраняем кириллицу
    safe_name = ''.join(c if c.isalnum() or c in '._-()[] ' or ord(c) > 127 else '_' for c in name)
    return get_valid_filename(translit(safe_name, 'ru', reversed=True)) + ext


def assignment_file_path(instance, filename):
    safe_filename = sanitize_filename(filename)
    return f'assignments/{instance.assignment.id}/{safe_filename}'

class AssignmentFile(models.Model):
    """Файл, прикреплённый к заданию (материалы ДЗ)"""
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='files'
    )
    file = models.FileField('Файл', upload_to=assignment_file_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Файл для {self.assignment.title}'


class StudentAssignment(models.Model):
    """Назначение задания конкретному ученику с индивидуальным дедлайном"""
    class Status(models.TextChoices):
        ASSIGNED = 'assigned', 'Назначено'
        SUBMITTED = 'submitted', 'Сдано'
        GRADED = 'graded', 'Проверено'

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='student_assignments'
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
        related_name='student_assignments'
    )
    deadline = models.DateTimeField('Срок сдачи')
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=Status.choices,
        default=Status.ASSIGNED
    )
    grade = models.PositiveSmallIntegerField('Оценка', null=True, blank=True)
    tutor_comment = models.TextField('Комментарий репетитора', blank=True)
    student_comment = models.TextField('Комментарий ученика', blank=True)
    submitted_at = models.DateTimeField('Время сдачи', null=True, blank=True)

    class Meta:
        verbose_name = 'Назначение ученику'
        verbose_name_plural = 'Назначения ученикам'
        constraints = [
            models.UniqueConstraint(
                fields=['assignment', 'student'],
                name='unique_assignment_student'
            )
        ]
        ordering = ['deadline']

    def __str__(self):
        return f'{self.student} → {self.assignment.title}'

    def clean(self):
        if self.student.role != 'student':
            raise ValidationError({'student': 'Пользователь должен быть учеником.'})

    def can_submit(self):
        return self.status == self.Status.ASSIGNED and timezone.now() <= self.deadline

    def submit(self):
        if not self.can_submit():
            raise ValidationError('Невозможно сдать: срок истёк или работа уже сдана.')
        self.status = self.Status.SUBMITTED
        self.submitted_at = timezone.now()
        self.save(update_fields=['status', 'submitted_at'])


def submission_file_path(instance, filename):
    safe_filename = sanitize_filename(filename)
    return f'submissions/{instance.student_assignment.id}/{safe_filename}'

class SubmissionFile(models.Model):
    """Файл с ответом ученика"""
    student_assignment = models.ForeignKey(
        StudentAssignment,
        on_delete=models.CASCADE,
        related_name='submission_files'
    )
    file = models.FileField('Файл ответа', upload_to=submission_file_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Ответ: {self.student_assignment}'
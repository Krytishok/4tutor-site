<!-- src/pages/tutor/StudentSubmissionReviewPage.vue -->
<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getStudentAssignmentDetail, gradeAssignment } from '@/api/assignments'
import type { StudentAssignment, SubmissionFile } from '@/types/assignments'
import { toApiError, downloadFile } from '@/api/http'

const route = useRoute()
const router = useRouter()

const studentAssignmentPk = Number(route.params.pk)
const studentAssignment = ref<StudentAssignment | null>(null)
const loading = ref(true)
const errorMsg = ref('')
const saveMsg = ref('')

// Форма оценки
const gradeForm = reactive({
  grade: null as number | null,
  tutor_comment: '',
})

const isSubmitting = ref(false)

const fileNameFromUrl = (url: string) => decodeURIComponent(url.split('/').pop() || 'файл')

const downloadSubmissionFile = (file: SubmissionFile) => {
  const downloadUrl = `/api/v1/assignments/submission-files/${file.id}/download/`
  downloadFile(downloadUrl, fileNameFromUrl(file.file))
}

// Загрузка данных
const fetchStudentAssignment = async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    studentAssignment.value = await getStudentAssignmentDetail(studentAssignmentPk)
    if (studentAssignment.value.grade !== null) {
      gradeForm.grade = studentAssignment.value.grade
    }
    if (studentAssignment.value.tutor_comment) {
      gradeForm.tutor_comment = studentAssignment.value.tutor_comment
    }
  } catch (e) {
    errorMsg.value = toApiError(e).message
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await fetchStudentAssignment()
})

// Сохранение оценки и комментария
const saveGradeAndComment = async () => {
  if (!studentAssignment.value) return
  
  isSubmitting.value = true
  saveMsg.value = ''
  
  try {
    const grade = gradeForm.grade !== null ? gradeForm.grade : undefined
    const comment = gradeForm.tutor_comment
    
    if (grade === undefined && !comment) {
      alert('Введите оценку или комментарий')
      isSubmitting.value = false
      return
    }
    
    // Если оценка не указана, но есть комментарий, используем текущую оценку
    const finalGrade = grade ?? (studentAssignment.value?.grade ?? 0)
    
    await gradeAssignment(studentAssignmentPk, finalGrade, comment)
    saveMsg.value = '✓ Оценка и комментарий сохранены'
    
    // Обновляем данные
    await fetchStudentAssignment()
  } catch (e) {
    alert(toApiError(e).message)
  } finally {
    isSubmitting.value = false
  }
}

// Статусы
const statusLabels: Record<string, string> = {
  assigned: 'Назначено',
  submitted: 'Сдано',
  graded: 'Проверено',
}

const statusClasses: Record<string, string> = {
  assigned: 'status-assigned',
  submitted: 'status-submitted',
  graded: 'status-graded',
}
</script>

<template>
  <div class="submission-review-page">
    <!-- Верхняя панель -->
    <header class="page-header">
      <button class="btn btn-outline" @click="router.back()">
        ← Назад к заданию
      </button>
      <div class="header-actions">
        <button
          class="btn btn-primary"
          @click="saveGradeAndComment"
          :disabled="isSubmitting || loading"
        >
          💾 Сохранить оценку
        </button>
      </div>
    </header>

    <!-- Сообщения -->
    <div v-if="loading" class="loading-state">Загрузка...</div>
    <div v-else-if="errorMsg" class="error-state">{{ errorMsg }}</div>
    <p v-if="saveMsg" class="success-message">{{ saveMsg }}</p>

    <template v-if="studentAssignment && !loading">
      <div class="review-grid">
        <!-- Информация о студенте и задании -->
        <section class="card info-card">
          <div class="card-header">
            <h2 class="card-title">Работа ученика</h2>
          </div>
          <div class="card-body">
            <div class="field">
              <label class="field-label">Ученик</label>
              <p class="field-value">
                {{ studentAssignment.student.first_name }} {{ studentAssignment.student.last_name }}
              </p>
            </div>
            <div class="field">
              <label class="field-label">Задание</label>
              <p class="field-value">{{ studentAssignment.assignment.title }}</p>
            </div>
            <div class="field">
              <label class="field-label">Предмет</label>
              <p class="field-value">{{ studentAssignment.assignment.subject }}</p>
            </div>
            <div class="field">
              <label class="field-label">Статус</label>
              <span
                class="status-chip"
                :class="statusClasses[studentAssignment.status]"
              >
                {{ statusLabels[studentAssignment.status] || studentAssignment.status }}
              </span>
            </div>
            <div class="field">
              <label class="field-label">Дедлайн</label>
              <p class="field-value">
                {{ new Date(studentAssignment.deadline).toLocaleString('ru-RU') }}
              </p>
            </div>
            <div v-if="studentAssignment.submitted_at" class="field">
              <label class="field-label">Сдано</label>
              <p class="field-value">
                {{ new Date(studentAssignment.submitted_at).toLocaleString('ru-RU') }}
              </p>
            </div>
          </div>
        </section>

        <!-- Файлы submission -->
        <section class="card files-card">
          <div class="card-header">
            <h2 class="card-title">📎 Файлы работы</h2>
          </div>
          <div class="card-body">
            <div v-if="studentAssignment.submission_files && studentAssignment.submission_files.length" class="file-list">
              <div
                v-for="file in studentAssignment.submission_files"
                :key="file.id"
                class="file-item"
              >
                <a target="_blank" class="file-link">
                  <span class="file-icon">📄</span>
                  <span class="file-name" @click="downloadSubmissionFile(file)">{{ fileNameFromUrl(file.file) }}</span>
                </a>
              </div>
            </div>
            <p v-else class="empty-hint">Файлы не загружены</p>
          </div>
        </section>

        <!-- Форма оценки -->
        <section class="card grade-card">
          <div class="card-header">
            <h2 class="card-title">📊 Оценка и комментарий</h2>
          </div>
          <div class="card-body">
            <div class="form-group">
              <label class="form-label">Оценка</label>
              <div class="grade-input-group">
                <input
                  type="number"
                  v-model.number="gradeForm.grade"
                  class="input input-lg"
                  :min="0"
                  :max="studentAssignment.assignment.max_grade"
                  placeholder="0"
                />
                <span class="max-grade">/ {{ studentAssignment.assignment.max_grade }}</span>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Комментарий репетитора</label>
              <textarea
                v-model="gradeForm.tutor_comment"
                class="textarea"
                rows="6"
                placeholder="Напишите комментарий к работе ученика..."
              ></textarea>
            </div>

            <div class="current-grade-info" v-if="studentAssignment.grade !== null">
              <strong>Текущая оценка:</strong> {{ studentAssignment.grade }} / {{ studentAssignment.assignment.max_grade }}
            </div>
          </div>
        </section>
      </div>
    </template>
  </div>
</template>

<style scoped>
.submission-review-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.loading-state,
.error-state {
  text-align: center;
  padding: 2rem;
  font-size: 1.1rem;
}

.error-state {
  color: #dc3545;
}

.success-message {
  background: #d4edda;
  color: #155724;
  padding: 0.75rem 1rem;
  border-radius: 4px;
  margin-bottom: 1.5rem;
}

.review-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
}

.card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.card-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e9ecef;
  background: #f8f9fa;
}

.card-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #212529;
}

.card-body {
  padding: 1.5rem;
}

.field {
  margin-bottom: 1rem;
}

.field:last-child {
  margin-bottom: 0;
}

.field-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #6c757d;
  margin-bottom: 0.25rem;
}

.field-value {
  font-size: 1rem;
  color: #212529;
  margin: 0;
}

.status-chip {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
}

.status-assigned {
  background: #e9ecef;
  color: #495057;
}

.status-submitted {
  background: #cce5ff;
  color: #004085;
}

.status-graded {
  background: #d4edda;
  color: #155724;
}

.file-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 4px;
}

.file-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #007bff;
  text-decoration: none;
}

.file-link:hover {
  text-decoration: underline;
}

.file-icon {
  font-size: 1.25rem;
}

.file-name {
  font-size: 0.95rem;
  color: #212529;
}

.empty-hint {
  color: #6c757d;
  font-style: italic;
  text-align: center;
  padding: 1rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-label {
  display: block;
  font-size: 0.95rem;
  font-weight: 500;
  color: #212529;
  margin-bottom: 0.5rem;
}

.grade-input-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.input-lg {
  width: 100px;
  padding: 0.75rem;
  font-size: 1.25rem;
  border: 2px solid #dee2e6;
  border-radius: 4px;
}

.input-lg:focus {
  outline: none;
  border-color: #007bff;
}

.max-grade {
  font-size: 1.25rem;
  font-weight: 500;
  color: #6c757d;
}

.textarea {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #dee2e6;
  border-radius: 4px;
  font-size: 1rem;
  font-family: inherit;
  resize: vertical;
}

.textarea:focus {
  outline: none;
  border-color: #007bff;
}

.current-grade-info {
  margin-top: 1rem;
  padding: 0.75rem;
  background: #e9ecef;
  border-radius: 4px;
  font-size: 0.95rem;
  color: #495057;
}

.btn {
  padding: 0.625rem 1.25rem;
  border-radius: 4px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-outline {
  background: transparent;
  border: 2px solid #6c757d;
  color: #6c757d;
}

.btn-outline:hover:not(:disabled) {
  background: #6c757d;
  color: #fff;
}

.btn-primary {
  background: #007bff;
  color: #fff;
}

.btn-primary:hover:not(:disabled) {
  background: #0056b3;
}
</style>

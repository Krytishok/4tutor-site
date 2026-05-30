<!-- src/pages/student/AssignmentDetailPage.vue -->
<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getStudentAssignmentDetail, submitAssignment, uploadSubmissionFile } from '@/api/assignments'
import type { StudentAssignment, AssignmentFile, SubmissionFile } from '@/types/assignments'
import { toApiError, downloadFile } from '@/api/http'

const route = useRoute()
const router = useRouter()
const pk = Number(route.params.id)
const sa = ref<StudentAssignment | null>(null)
const loading = ref(false)
const errorMsg = ref('')
const submitting = ref(false)
const uploadLoading = ref(false)

// Подтверждение отправки
const showConfirmDialog = ref(false)

const fileNameFromUrl = (url: string) => decodeURIComponent(url.split('/').pop() || 'файл')

const downloadAssignmentFile = (file: AssignmentFile) => {
  // Используем новый защищённый эндпоинт
  const downloadUrl = `/api/v1/assignments/assignment-files/${file.id}/download/`
  downloadFile(downloadUrl, fileNameFromUrl(file.file))
}

const downloadSubmissionFile = (file: SubmissionFile) => {
  const downloadUrl = `/api/v1/assignments/submission-files/${file.id}/download/`
  downloadFile(downloadUrl, fileNameFromUrl(file.file))
}

// Таймер для пересчёта оставшегося времени
const now = ref(Date.now())
let timer: ReturnType<typeof setInterval> | null = null

const fetch = async () => {
  loading.value = true
  try {
    sa.value = await getStudentAssignmentDetail(pk)
  } catch (e) {
    errorMsg.value = toApiError(e).message
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  if (!sa.value || sa.value.status !== 'assigned') return
  submitting.value = true
  try {
    await submitAssignment(sa.value.id)
    showConfirmDialog.value = false
    await fetch()
  } catch (e) {
    alert(toApiError(e).message)
  } finally {
    submitting.value = false
  }
}

const handleFileUpload = async (e: Event) => {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file || !sa.value) return
  uploadLoading.value = true
  try {
    await uploadSubmissionFile(sa.value.id, file)
    await fetch()
  } catch (e) {
    alert(toApiError(e).message)
  } finally {
    uploadLoading.value = false
  }
}

const canSubmitComputed = computed(() => {
  if (!sa.value || sa.value.status !== 'assigned') return false
  return new Date(sa.value.deadline).getTime() > now.value
})

const deadlineMs = computed(() => {
  if (!sa.value) return 0
  return new Date(sa.value.deadline).getTime() - now.value
})

const deadlineRemaining = computed(() => {
  const diff = deadlineMs.value
  if (diff <= 0) return 'Срок истёк'
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
  let parts = []
  if (days > 0) parts.push(`${days} д`)
  if (hours > 0) parts.push(`${hours} ч`)
  if (minutes > 0 || parts.length === 0) parts.push(`${minutes} мин`)
  return 'Осталось: ' + parts.join(' ')
})

const deadlineUrgency = computed(() => {
  const diff = deadlineMs.value
  if (diff <= 0) return 'expired'   // красный
  if (diff < 24 * 60 * 60 * 1000) return 'soon' // оранжевый (< 1 дня)
  return 'normal'
})

const statusLabel = computed(() => {
  if (!sa.value) return ''
  const map = { assigned: 'Назначено', submitted: 'Сдано', graded: 'Проверено' }
  return map[sa.value.status] || sa.value.status
})

const statusClass = computed(() => {
  if (!sa.value) return ''
  return {
    assigned: deadlineUrgency.value === 'expired' ? 'chip-danger' : 'chip-warning',
    submitted: 'chip-warning',
    graded: 'chip-success'
  }[sa.value.status] || ''
})

const formatDeadline = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('ru-RU', {
    day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit'
  })
}

onMounted(() => {
  fetch()
  // Обновляем таймер каждые 30 секунд
  timer = setInterval(() => { now.value = Date.now() }, 30000)
})

onBeforeUnmount(() => {
  if (timer) clearInterval(timer)
})
</script>

<template>
  <div class="page">
    <button class="btn" @click="router.back()">← Назад</button>

    <div v-if="loading" class="muted">Загрузка...</div>
    <div v-else-if="errorMsg" class="chip chip-danger">{{ errorMsg }}</div>

    <template v-if="sa">
      <div class="assignment-header">
        <h1 class="page-title">{{ sa.assignment?.title || 'Задание' }}</h1>
        <span class="chip" :class="statusClass">{{ statusLabel }}</span>
      </div>

      <div v-if="sa.assignment?.subject" class="subject-badge">
        {{ sa.assignment.subject }}
      </div>

      <!-- Блок дедлайна с обратным отсчётом -->
      <div class="card deadline-card" :class="'deadline-' + deadlineUrgency">
        <div class="card-title">⏰ Дедлайн</div>
        <p class="deadline-date">{{ formatDeadline(sa.deadline) }}</p>
        <p v-if="deadlineMs > 0" class="deadline-countdown">{{ deadlineRemaining }}</p>
        <p v-else class="deadline-warning">Срок сдачи истёк</p>
      </div>

      <!-- Блок описания задания -->
      <div v-if="sa.assignment?.description" class="card description-card">
        <div class="card-title">📋 Описание задания</div>
        <p class="description-text">{{ sa.assignment.description }}</p>
      </div>

      <!-- Файлы задания -->
      <div v-if="sa.assignment?.files?.length" class="card">
        <div class="card-title">📂 Файлы задания</div>
        <div class="file-list">
          <a
            v-for="f in sa.assignment.files" :key="f.id"
            target="_blank" class="file-item"
            :title="f.file.split('/').pop()"
          >
            <span class="file-icon">📄</span>
            <span class="file-name" @click="downloadAssignmentFile(f)">{{ fileNameFromUrl(f.file) }}</span>
          </a>
        </div>
      </div>

      <!-- Комментарий и оценка -->
      <div v-if="sa.tutor_comment || sa.grade !== null" class="card feedback-card">
        <div class="card-title">💬 Обратная связь</div>
        <p v-if="sa.tutor_comment" class="comment">{{ sa.tutor_comment }}</p>
        <div v-if="sa.grade !== null" class="grade-badge">
          Оценка: <strong>{{ sa.grade }}</strong>
        </div>
      </div>

      <!-- Файлы ответа ученика -->
      <div class="card">
        <div class="card-title">📎 Мои ответы</div>
        <div v-if="sa.submission_files?.length" class="file-list">
          <a
            v-for="f in sa.submission_files" :key="f.id"
            target="_blank" class="file-item"
            :title="f.file.split('/').pop()"
          >
            <span class="file-icon">📄</span>
            <span class="file-name" @click="downloadSubmissionFile(f)">{{ fileNameFromUrl(f.file) }}</span>
          </a>
        </div>
        <p v-else class="muted">Файлов пока нет</p>

        <div v-if="sa.status === 'assigned'" class="upload-area">
          <label class="btn btn-primary upload-btn">
            <span>Загрузить файл</span>
            <input type="file" hidden @change="handleFileUpload" :disabled="uploadLoading" />
          </label>
        </div>
      </div>

      <!-- Кнопка отправки -->
      <div v-if="canSubmitComputed" class="submit-section">
        <button class="btn btn-primary submit-btn" @click="showConfirmDialog = true" :disabled="submitting">
          {{ submitting ? 'Отправка...' : 'Отправить работу' }}
        </button>
        <p class="muted submit-hint">После отправки изменить файлы будет нельзя.</p>
      </div>
    </template>

    <!-- Модальное окно подтверждения -->
    <Teleport to="body">
      <div v-if="showConfirmDialog" class="dialog-overlay" @click.self="showConfirmDialog = false">
        <div class="dialog-card">
          <h3 class="dialog-title">Подтвердите отправку</h3>
          <p class="dialog-text">Вы уверены, что хотите отправить работу? После отправки вы больше не сможете изменить свои файлы.</p>
          <div class="dialog-actions">
            <button class="btn" @click="showConfirmDialog = false">Отмена</button>
            <button class="btn btn-primary" @click="handleSubmit" :disabled="submitting">
              Да, отправить
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
/* Увеличенная страница */
.page {
  max-width: 840px;
  margin: 0 auto;
  gap: 20px;
}

.assignment-header {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 12px;
}

.subject-badge {
  display: inline-block;
  background: rgba(30, 58, 138, 0.08);
  color: var(--primary);
  border-radius: 8px;
  padding: 6px 14px;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 4px;
}

/* Дедлайн */
.deadline-card {
  border-left: 6px solid var(--primary);
  padding: 18px;
  transition: border-color 0.2s, background 0.2s;
}
.deadline-card.deadline-expired {
  border-left-color: var(--danger);
  background: #fff5f5;
}
.deadline-card.deadline-soon {
  border-left-color: var(--reminder);
  background: #fffbeb;
}
.deadline-date {
  font-size: 20px;
  font-weight: 700;
  margin: 4px 0;
}
.deadline-countdown {
  font-size: 16px;
  font-weight: 600;
  color: var(--muted);
  margin: 0;
}
.deadline-warning {
  color: var(--danger);
  font-weight: 600;
  font-size: 16px;
  margin: 4px 0 0;
}

/* Описание */
.description-card {
  padding: 20px;
  background: var(--panel);
}
.description-text {
  white-space: pre-wrap;
  font-size: 15px;
  line-height: 1.6;
  color: var(--text);
}

/* Файлы */
.file-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: var(--radius-sm);
  background: var(--bg);
  border: 1px solid var(--border);
  text-decoration: none;
  color: var(--text);
  transition: background 0.15s, border-color 0.15s;
  cursor: pointer;
  max-width: 100%;
  overflow: hidden;
}
.file-item:hover {
  background: rgba(30, 58, 138, 0.04);
  border-color: rgba(30, 58, 138, 0.35);
}
.file-icon {
  font-size: 20px;
  flex-shrink: 0;
}
.file-name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-weight: 500;
  font-size: 14px;
}

/* Обратная связь */
.feedback-card .comment {
  white-space: pre-wrap;
  font-size: 15px;
  margin: 0 0 10px 0;
}
.grade-badge {
  display: inline-block;
  background: var(--primary);
  color: #fff;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 18px;
  font-weight: 700;
}

/* Загрузка */
.upload-area {
  margin-top: 16px;
}
.upload-btn {
  gap: 6px;
}

/* Отправка */
.submit-section {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
  margin-top: 4px;
}
.submit-btn {
  font-size: 16px;
  padding: 14px 28px;
}
.submit-hint {
  font-size: 13px;
}

/* Модальное окно */
.dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(2px);
}
.dialog-card {
  background: var(--panel);
  padding: 24px;
  border-radius: var(--radius-lg);
  max-width: 420px;
  width: 90%;
  box-shadow: 0 20px 40px rgba(0,0,0,0.15);
}
.dialog-title {
  margin: 0 0 12px 0;
  font-size: 20px;
  font-weight: 700;
  color: var(--primary);
}
.dialog-text {
  margin: 0 0 20px 0;
  color: var(--text);
  line-height: 1.5;
}
.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
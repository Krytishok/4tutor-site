<!-- src/pages/student/AssignmentDetailPage.vue -->
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getStudentAssignmentDetail, submitAssignment, uploadSubmissionFile } from '@/api/assignments'
import type { StudentAssignment } from '@/types/assignments'
import { toApiError } from '@/api/http'

const route = useRoute()
const router = useRouter()
const pk = Number(route.params.id)
const sa = ref<StudentAssignment | null>(null)
const loading = ref(false)
const errorMsg = ref('')
const submitting = ref(false)
const uploadLoading = ref(false)

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

const canSubmit = () => {
  if (!sa.value || sa.value.status !== 'assigned') return false
  return new Date(sa.value.deadline) > new Date()
}

onMounted(fetch)
</script>

<template>
  <div class="page">
    <button class="btn" @click="router.back()">← Назад</button>

    <div v-if="loading" class="muted">Загрузка...</div>
    <div v-else-if="errorMsg" class="chip chip-danger">{{ errorMsg }}</div>

    <template v-if="sa">
      <h1 class="page-title">{{ sa.assignment_title || 'Задание' }}</h1>

      <div class="card">
        <div class="card-title">Дедлайн</div>
        <p>{{ new Date(sa.deadline).toLocaleString() }}</p>
        <span class="chip" :class="sa.status === 'graded' ? 'chip-success' : sa.status === 'submitted' ? 'chip-warning' : ''">
          {{ sa.status }}
        </span>
      </div>

      <div v-if="sa.tutor_comment" class="card">
        <div class="card-title">Комментарий репетитора</div>
        <p>{{ sa.tutor_comment }}</p>
        <p v-if="sa.grade !== null">Оценка: {{ sa.grade }}</p>
      </div>

      <div class="card">
        <div class="card-title">Мои файлы ответа</div>
        <ul v-if="sa.submission_files?.length">
          <li v-for="f in sa.submission_files" :key="f.id">
            <a :href="f.file" target="_blank">{{ f.file.split('/').pop() }}</a>
          </li>
        </ul>
        <p v-else class="muted">Файлов пока нет</p>
        <div v-if="sa.status === 'assigned'">
          <label class="btn" style="cursor:pointer; margin-top:8px;">
            Загрузить файл
            <input type="file" hidden @change="handleFileUpload" :disabled="uploadLoading" />
          </label>
        </div>
      </div>

      <div v-if="canSubmit()" style="margin-top:12px;">
        <button class="btn btn-primary" @click="handleSubmit" :disabled="submitting">
          {{ submitting ? 'Отправка...' : 'Отправить работу' }}
        </button>
        <p class="muted" style="margin-top:4px;">После отправки изменить файлы будет нельзя.</p>
      </div>
    </template>
  </div>
</template>
<!-- src/pages/tutor/AssignmentsPage.vue -->
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getAssignments, createAssignment } from '@/api/assignments'
import type { AssignmentListItem } from '@/types/assignments'
import { toApiError } from '@/api/http'
import BaseModal from '@/components/ui/BaseModal.vue'

const router = useRouter()
const assignments = ref<AssignmentListItem[]>([])
const loading = ref(false)
const errorMsg = ref('')
const showCreateModal = ref(false)

const formTitle = ref('')
const formDescription = ref('')
const formSubject = ref('')
const formDeadline = ref('')
const formFiles = ref<File[]>([])
const creating = ref(false)

const fetchAssignments = async () => {
  loading.value = true
  try {
    assignments.value = await getAssignments()
  } catch (e) {
    errorMsg.value = toApiError(e).message
  } finally {
    loading.value = false
  }
}

const handleCreate = async () => {
  if (!formTitle.value) return
  creating.value = true
  try {
    await createAssignment({
      title: formTitle.value,
      description: formDescription.value || undefined,
      subject: formSubject.value || undefined,
      deadline: formDeadline.value || undefined,
      files: formFiles.value.length ? formFiles.value : undefined,
    })
    showCreateModal.value = false
    resetForm()
    await fetchAssignments()
  } catch (e) {
    alert(toApiError(e).message)
  } finally {
    creating.value = false
  }
}

const resetForm = () => {
  formTitle.value = ''
  formDescription.value = ''
  formSubject.value = ''
  formDeadline.value = ''
  formFiles.value = []
}

const onFileChange = (e: Event) => {
  const input = e.target as HTMLInputElement
  if (input.files) formFiles.value = Array.from(input.files)
}

const goToDetail = (id: number) => router.push(`/app/tutor/assignments/${id}`)

onMounted(fetchAssignments)
</script>

<template>
  <div class="page">
    <div class="row">
      <div>
        <h1 class="page-title">Задания</h1>
        <p class="muted">Создавайте домашние задания и отслеживайте выполнение.</p>
      </div>
      <button class="btn btn-primary" @click="showCreateModal = true">+ Создать задание</button>
    </div>

    <div v-if="errorMsg" class="card chip chip-danger">{{ errorMsg }}</div>
    <div v-if="loading" class="muted">Загрузка...</div>

    <div v-else-if="assignments.length === 0" class="card muted">Заданий пока нет. Создайте первое.</div>

    <div v-else class="card">
      <div class="card-title">Список заданий</div>
      <div style="overflow-x: auto;">
        <table class="table">
          <thead>
            <tr>
              <th>Название</th>
              <th>Предмет</th>
              <th>Создано</th>
              <th>Файлы</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="a in assignments" :key="a.id" @click="goToDetail(a.id)" style="cursor: pointer;">
              <td>{{ a.title }}</td>
              <td>{{ a.subject || '—' }}</td>
              <td>{{ new Date(a.created_at).toLocaleDateString() }}</td>
              <td>{{ a.files_count }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <BaseModal :show="showCreateModal" @close="showCreateModal = false">
      <h2 style="margin-top:0;">Новое задание</h2>
      <form class="form" @submit.prevent="handleCreate">
        <label class="label">Название *</label>
        <input v-model="formTitle" class="input" placeholder="Например, Домашняя работа №1" required />
        <label class="label">Предмет</label>
        <input v-model="formSubject" class="input" placeholder="Алгебра" />
        <label class="label">Описание</label>
        <textarea v-model="formDescription" class="input" rows="3" placeholder="Пояснения..." />
        <label class="label">Общий дедлайн</label>
        <input v-model="formDeadline" type="datetime-local" class="input" />
        <label class="label">Файлы материалов</label>
        <input type="file" multiple @change="onFileChange" class="input" />
        <div class="row" style="justify-content: flex-end; margin-top: 12px;">
          <button type="button" class="btn" @click="showCreateModal = false">Отмена</button>
          <button type="submit" class="btn btn-primary" :disabled="creating || !formTitle">
            {{ creating ? 'Создаётся...' : 'Создать' }}
          </button>
        </div>
      </form>
    </BaseModal>
  </div>
</template>
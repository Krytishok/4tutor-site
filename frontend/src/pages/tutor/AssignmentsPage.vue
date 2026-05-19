<!-- src/pages/tutor/AssignmentsPage.vue -->
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getAssignments, createAssignment, type AssignmentFilters } from '@/api/assignments'
import type { AssignmentListItem } from '@/types/assignments'
import { toApiError } from '@/api/http'
import BaseModal from '@/components/ui/BaseModal.vue'

const router = useRouter()
const assignments = ref<AssignmentListItem[]>([])
const loading = ref(false)
const errorMsg = ref('')
const showCreateModal = ref(false)

// Pagination state
const currentPage = ref(1)
const pageSize = ref(15)
const totalItems = ref(0)
const totalPages = ref(0)

// Filter state
const searchQuery = ref('')
const subjectFilter = ref('')
const deadlineBefore = ref('')
const deadlineAfter = ref('')
const statusFilter = ref('')

// Form fields
const formTitle = ref('')
const formDescription = ref('')
const formSubject = ref('')
const formFiles = ref<File[]>([])
const creating = ref(false)

const fetchAssignments = async () => {
  loading.value = true
  try {
    const filters: AssignmentFilters = {
      page: currentPage.value,
      page_size: pageSize.value,
    }
    if (searchQuery.value) filters.search = searchQuery.value
    if (subjectFilter.value) filters.subject = subjectFilter.value
    if (deadlineBefore.value) filters.deadline_before = deadlineBefore.value
    if (deadlineAfter.value) filters.deadline_after = deadlineAfter.value
    if (statusFilter.value) filters.status = statusFilter.value

    const response = await getAssignments(filters)
    assignments.value = response.results
    totalItems.value = response.pagination.total
    totalPages.value = response.pagination.total_pages
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
      files: formFiles.value.length ? formFiles.value : undefined,
      // deadline и students не передаём
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
  formFiles.value = []
}

const onFileChange = (e: Event) => {
  const input = e.target as HTMLInputElement
  if (input.files) formFiles.value = Array.from(input.files)
}

const goToDetail = (id: number) => router.push(`/app/tutor/assignments/${id}`)

const applyFilters = () => {
  currentPage.value = 1
  fetchAssignments()
}

const clearFilters = () => {
  searchQuery.value = ''
  subjectFilter.value = ''
  deadlineBefore.value = ''
  deadlineAfter.value = ''
  statusFilter.value = ''
  currentPage.value = 1
  fetchAssignments()
}

const changePage = (newPage: number) => {
  if (newPage < 1 || newPage > totalPages.value) return
  currentPage.value = newPage
  fetchAssignments()
}

onMounted(fetchAssignments)
</script>

<template>
  <div class="page">
    <div class="row" style="justify-content: space-between; align-items: flex-start;">
      <div>
        <h1 class="page-title">Задания</h1>
        <p class="muted">Создавайте домашние задания и отслеживайте выполнение.</p>
      </div>
      <button class="btn btn-primary" @click="showCreateModal = true">+ Создать задание</button>
    </div>

    <!-- Компактный блок фильтров в одну строку -->
    <div class="card" style="padding: 16px 20px; margin-top: 16px;">
      <div style="display: flex; flex-wrap: wrap; align-items: flex-end; gap: 12px;">
        <div style="min-width: 160px; flex: 1;">
          <label class="label" style="margin-bottom: 4px;">Поиск</label>
          <input v-model="searchQuery" class="input" placeholder="Название..." />
        </div>
        <div style="min-width: 140px; flex: 1;">
          <label class="label" style="margin-bottom: 4px;">Предмет</label>
          <input v-model="subjectFilter" class="input" placeholder="Алгебра..." />
        </div>
        <div style="min-width: 140px; flex: 1;">
          <label class="label" style="margin-bottom: 4px;">Дедлайн до</label>
          <input v-model="deadlineBefore" type="date" class="input" />
        </div>
        <div style="min-width: 140px; flex: 1;">
          <label class="label" style="margin-bottom: 4px;">Дедлайн после</label>
          <input v-model="deadlineAfter" type="date" class="input" />
        </div>
        <div style="min-width: 140px; flex: 1;">
          <label class="label" style="margin-bottom: 4px;">Статус</label>
          <select v-model="statusFilter" class="input">
            <option value="">Все статусы</option>
            <option value="assigned">Назначено</option>
            <option value="submitted">Сдано</option>
            <option value="graded">Проверено</option>
          </select>
        </div>
        <div style="display: flex; gap: 8px; align-items: flex-end; padding-bottom: 2px;">
          <button class="btn btn-primary" @click="applyFilters" style="white-space: nowrap;">
            Применить
          </button>
          <button
            v-if="searchQuery || subjectFilter || deadlineBefore || deadlineAfter || statusFilter"
            class="btn"
            @click="clearFilters"
            style="white-space: nowrap;"
          >
            Сбросить
          </button>
        </div>
      </div>
    </div>

    <div v-if="errorMsg" class="card chip chip-danger">{{ errorMsg }}</div>
    <div v-if="loading" class="muted">Загрузка...</div>

    <div v-else-if="assignments.length === 0" class="card muted">
      Заданий пока нет. Создайте первое.
    </div>

    <div v-else class="card">
      <div class="card-title">Список заданий ({{ totalItems }} всего)</div>
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

      <!-- Pagination -->
      <div class="row" style="justify-content: space-between; align-items: center; margin-top: 16px;">
        <div class="muted">
          Страница {{ currentPage }} из {{ totalPages }} ({{ totalItems }} заданий)
        </div>
        <div class="row" style="gap: 8px;">
          <button
            class="btn"
            @click="changePage(currentPage - 1)"
            :disabled="currentPage <= 1"
          >
            ← Назад
          </button>
          <button
            class="btn"
            @click="changePage(currentPage + 1)"
            :disabled="currentPage >= totalPages"
          >
            Вперёд →
          </button>
        </div>
      </div>
    </div>

    <!-- Простая форма создания (без дедлайна и выбора учеников) -->
    <BaseModal :show="showCreateModal" @close="showCreateModal = false">
      <h2 style="margin-top:0;">Новое задание</h2>
      <form class="form" @submit.prevent="handleCreate">
        <label class="label">Название *</label>
        <input v-model="formTitle" class="input" placeholder="Например, Домашняя работа №1" required />
        <label class="label">Предмет</label>
        <input v-model="formSubject" class="input" placeholder="Алгебра" />
        <label class="label">Описание</label>
        <textarea v-model="formDescription" class="input" rows="3" placeholder="Пояснения..." />
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
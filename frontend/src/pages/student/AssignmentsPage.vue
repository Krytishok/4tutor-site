<!-- src/pages/student/AssignmentsPage.vue -->
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getStudentAssignments, type AssignmentFilters } from '@/api/assignments'
import type { StudentAssignmentListItem } from '@/types/assignments'
import { toApiError } from '@/api/http'

const router = useRouter()
const items = ref<StudentAssignmentListItem[]>([])
const loading = ref(false)
const errorMsg = ref('')

// Пагинация
const currentPage = ref(1)
const pageSize = ref(15)
const totalItems = ref(0)
const totalPages = ref(0)

// Фильтры
const searchQuery = ref('')
const subjectFilter = ref('')
const deadlineBefore = ref('')
const deadlineAfter = ref('')
const statusFilter = ref('')

const fetch = async () => {
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

    const response = await getStudentAssignments(filters)
    items.value = response.results
    totalItems.value = response.pagination.total
    totalPages.value = response.pagination.total_pages
  } catch (e) {
    errorMsg.value = toApiError(e).message
  } finally {
    loading.value = false
  }
}

const statusChip = (status: string) => {
  switch (status) {
    case 'graded': return 'chip-success'
    case 'submitted': return 'chip-warning'
    default: return ''
  }
}

const goToDetail = (id: number) => router.push(`/app/student/assignments/${id}`)

const applyFilters = () => {
  currentPage.value = 1
  fetch()
}

const clearFilters = () => {
  searchQuery.value = ''
  subjectFilter.value = ''
  deadlineBefore.value = ''
  deadlineAfter.value = ''
  statusFilter.value = ''
  currentPage.value = 1
  fetch()
}

const changePage = (newPage: number) => {
  if (newPage < 1 || newPage > totalPages.value) return
  currentPage.value = newPage
  fetch()
}

onMounted(fetch)
</script>

<template>
  <div class="page">
    <h1 class="page-title">Мои задания</h1>
    <p class="muted">Задания от репетиторов</p>

    <!-- Компактный блок фильтров в одну строку (как у репетитора) -->
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

    <div v-if="loading" class="muted">Загрузка...</div>
    <div v-else-if="errorMsg" class="chip chip-danger">{{ errorMsg }}</div>
    <div v-else-if="items.length === 0" class="card muted">Активных заданий нет</div>

    <div v-else class="card">
      <div class="card-title">Список заданий ({{ totalItems }} всего)</div>
      <div style="overflow-x: auto;">
        <table class="table">
          <thead>
            <tr>
              <th>Задание</th>
              <th>Репетитор</th>
              <th>Дедлайн</th>
              <th>Статус</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="sa in items" :key="sa.id" @click="goToDetail(sa.id)" style="cursor:pointer;">
              <td>{{ sa.assignment_title }}</td>
              <td>{{ sa.tutor.first_name }} {{ sa.tutor.last_name }}</td>
              <td>{{ new Date(sa.deadline).toLocaleString() }}</td>
              <td><span class="chip" :class="statusChip(sa.status)">{{ sa.status }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Пагинация -->
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
  </div>
</template>
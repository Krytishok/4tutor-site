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

    <!-- Filters Section -->
    <div class="card" style="margin-top: 20px;">
      <div class="card-title" style="display: flex; justify-content: space-between; align-items: center;">
        <span>Фильтры</span>
        <button class="btn btn-sm" @click="clearFilters" v-if="searchQuery || subjectFilter || deadlineBefore || deadlineAfter || statusFilter">
          Сбросить
        </button>
      </div>
      <div class="grid grid-cols-4" style="gap: 16px; margin-top: 16px;">
        <div>
          <label class="label">Поиск</label>
          <input v-model="searchQuery" class="input" placeholder="Название..." />
        </div>
        <div>
          <label class="label">Предмет</label>
          <input v-model="subjectFilter" class="input" placeholder="Алгебра..." />
        </div>
        <div>
          <label class="label">Дедлайн до</label>
          <input v-model="deadlineBefore" type="date" class="input" />
        </div>
        <div>
          <label class="label">Дедлайн после</label>
          <input v-model="deadlineAfter" type="date" class="input" />
        </div>
      </div>
      <div class="grid grid-cols-4" style="gap: 16px; margin-top: 16px;">
        <div>
          <label class="label">Статус</label>
          <select v-model="statusFilter" class="input">
            <option value="">Все статусы</option>
            <option value="assigned">Назначено</option>
            <option value="submitted">Сдано</option>
            <option value="graded">Проверено</option>
          </select>
        </div>
      </div>
      <div class="row" style="margin-top: 16px;">
        <button class="btn btn-primary" @click="applyFilters">Применить фильтры</button>
      </div>
    </div>

    <div v-if="loading" class="muted">Загрузка...</div>
    <div v-else-if="errorMsg" class="chip chip-danger">{{ errorMsg }}</div>
    <div v-else-if="items.length === 0" class="card muted">Активных заданий нет</div>

    <div v-else class="card">
      <div class="card-title">Список заданий ({{ totalItems }} всего)</div>
      <table class="table">
        <thead>
          <tr><th>Задание</th><th>Дедлайн</th><th>Статус</th></tr>
        </thead>
        <tbody>
          <tr v-for="sa in items" :key="sa.id" @click="goToDetail(sa.id)" style="cursor:pointer;">
            <td>{{ sa.assignment_title }}</td>
            <td>{{ new Date(sa.deadline).toLocaleString() }}</td>
            <td><span class="chip" :class="statusChip(sa.status)">{{ sa.status }}</span></td>
          </tr>
        </tbody>
      </table>
      
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
  </div>
</template>
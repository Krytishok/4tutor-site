<!-- src/pages/student/AssignmentsPage.vue -->
<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { getStudentAssignments } from '@/api/assignments'
import type { StudentAssignmentListItem, StudentAssignmentFilterParams } from '@/types/assignments'
import { toApiError } from '@/api/http'

const router = useRouter()
const items = ref<StudentAssignmentListItem[]>([])
const loading = ref(false)
const errorMsg = ref('')

// Пагинация
const currentPage = ref(1)
const pageSize = ref(20)
const totalCount = ref(0)
const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value))

// Фильтры
const filterSubject = ref('')
const filterTitle = ref('')
const filterStatus = ref('')
const filterOrdering = ref('deadline')

const fetch = async () => {
  loading.value = true
  try {
    const params: StudentAssignmentFilterParams = {
      page: currentPage.value,
      page_size: pageSize.value,
      ordering: filterOrdering.value,
    }
    if (filterSubject.value) params.subject = filterSubject.value
    if (filterTitle.value) params.title = filterTitle.value
    if (filterStatus.value) params.status = filterStatus.value as 'assigned' | 'submitted' | 'graded'
    
    const response = await getStudentAssignments(params)
    items.value = response.results
    totalCount.value = response.count
  } catch (e) {
    errorMsg.value = toApiError(e).message
  } finally {
    loading.value = false
  }
}

const applyFilters = () => {
  currentPage.value = 1
  fetch()
}

const goToPage = (page: number) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  fetch()
}

const statusChip = (status: string) => {
  switch (status) {
    case 'graded': return 'chip-success'
    case 'submitted': return 'chip-warning'
    default: return ''
  }
}

const goToDetail = (id: number) => router.push(`/app/student/assignments/${id}`)

onMounted(fetch)
</script>

<template>
  <div class="page">
    <h1 class="page-title">Мои задания</h1>
    <p class="muted">Задания от репетиторов</p>

    <!-- Фильтры -->
    <div class="card">
      <div class="row" style="flex-wrap: wrap; gap: 12px;">
        <div style="flex: 1; min-width: 200px;">
          <label class="label">Поиск по названию</label>
          <input v-model="filterTitle" class="input" placeholder="Название задания..." @keyup.enter="applyFilters" />
        </div>
        <div style="flex: 1; min-width: 200px;">
          <label class="label">Предмет</label>
          <input v-model="filterSubject" class="input" placeholder="Например, Алгебра..." @keyup.enter="applyFilters" />
        </div>
        <div style="flex: 1; min-width: 200px;">
          <label class="label">Статус</label>
          <select v-model="filterStatus" class="input" @change="applyFilters">
            <option value="">Все статусы</option>
            <option value="assigned">Назначено</option>
            <option value="submitted">Сдано</option>
            <option value="graded">Проверено</option>
          </select>
        </div>
        <div style="flex: 1; min-width: 200px;">
          <label class="label">Сортировка</label>
          <select v-model="filterOrdering" class="input" @change="applyFilters">
            <option value="deadline">Дедлайн (возрастание)</option>
            <option value="-deadline">Дедлайн (убывание)</option>
            <option value="status">Статус</option>
            <option value="-status">Статус (обр.)</option>
            <option value="assignment__title">По названию (А-Я)</option>
            <option value="-assignment__title">По названию (Я-А)</option>
          </select>
        </div>
        <div style="display: flex; align-items: flex-end; gap: 8px;">
          <button class="btn btn-primary" @click="applyFilters">Применить</button>
          <button class="btn" @click="() => { filterTitle = ''; filterSubject = ''; filterStatus = ''; filterOrdering = 'deadline'; applyFilters() }">Сбросить</button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="muted">Загрузка...</div>
    <div v-else-if="errorMsg" class="chip chip-danger">{{ errorMsg }}</div>
    <div v-else-if="items.length === 0" class="card muted">Активных заданий нет</div>

    <div v-else class="card">
      <div class="card-title">Список заданий ({{ totalCount }})</div>
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
      
      <!-- Пагинация -->
      <div class="row" style="margin-top: 16px; justify-content: space-between; align-items: center;">
        <div class="muted">
          Показано {{ items.length }} из {{ totalCount }}
        </div>
        <div class="row" style="gap: 8px;">
          <button class="btn" :disabled="currentPage <= 1" @click="goToPage(currentPage - 1)">← Назад</button>
          <span class="chip">Стр. {{ currentPage }} из {{ totalPages }}</span>
          <button class="btn" :disabled="currentPage >= totalPages" @click="goToPage(currentPage + 1)">Вперёд →</button>
        </div>
      </div>
    </div>
  </div>
</template>
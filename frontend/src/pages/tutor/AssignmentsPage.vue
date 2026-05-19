<!-- src/pages/tutor/AssignmentsPage.vue -->
<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { getAssignments, createAssignment } from '@/api/assignments'
import type { AssignmentListItem, AssignmentFilterParams } from '@/types/assignments'
import { toApiError } from '@/api/http'
import BaseModal from '@/components/ui/BaseModal.vue'

const router = useRouter()
const assignments = ref<AssignmentListItem[]>([])
const loading = ref(false)
const errorMsg = ref('')
const showCreateModal = ref(false)

// Пагинация
const currentPage = ref(1)
const pageSize = ref(20)
const totalCount = ref(0)
const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value))

// Фильтры
const filterSubject = ref('')
const filterTitle = ref('')
const filterOrdering = ref('-created_at')

const formTitle = ref('')
const formDescription = ref('')
const formSubject = ref('')
const formFiles = ref<File[]>([])
const creating = ref(false)

const fetchAssignments = async () => {
  loading.value = true
  try {
    const params: AssignmentFilterParams = {
      page: currentPage.value,
      page_size: pageSize.value,
      ordering: filterOrdering.value,
    }
    if (filterSubject.value) params.subject = filterSubject.value
    if (filterTitle.value) params.title = filterTitle.value
    
    const response = await getAssignments(params)
    assignments.value = response.results
    totalCount.value = response.count
  } catch (e) {
    errorMsg.value = toApiError(e).message
  } finally {
    loading.value = false
  }
}

const applyFilters = () => {
  currentPage.value = 1
  fetchAssignments()
}

const goToPage = (page: number) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  fetchAssignments()
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
          <label class="label">Сортировка</label>
          <select v-model="filterOrdering" class="input" @change="applyFilters">
            <option value="-created_at">Сначала новые</option>
            <option value="created_at">Сначала старые</option>
            <option value="title">По названию (А-Я)</option>
            <option value="-title">По названию (Я-А)</option>
            <option value="subject">По предмету (А-Я)</option>
            <option value="-subject">По предмету (Я-А)</option>
          </select>
        </div>
        <div style="display: flex; align-items: flex-end; gap: 8px;">
          <button class="btn btn-primary" @click="applyFilters">Применить</button>
          <button class="btn" @click="() => { filterTitle = ''; filterSubject = ''; filterOrdering = '-created_at'; applyFilters() }">Сбросить</button>
        </div>
      </div>
    </div>

    <div v-if="errorMsg" class="card chip chip-danger">{{ errorMsg }}</div>
    <div v-if="loading" class="muted">Загрузка...</div>

    <div v-else-if="assignments.length === 0" class="card muted">Заданий пока нет. Создайте первое.</div>

    <div v-else class="card">
      <div class="card-title">Список заданий ({{ totalCount }})</div>
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
      
      <!-- Пагинация -->
      <div class="row" style="margin-top: 16px; justify-content: space-between; align-items: center;">
        <div class="muted">
          Показано {{ assignments.length }} из {{ totalCount }}
        </div>
        <div class="row" style="gap: 8px;">
          <button class="btn" :disabled="currentPage <= 1" @click="goToPage(currentPage - 1)">← Назад</button>
          <span class="chip">Стр. {{ currentPage }} из {{ totalPages }}</span>
          <button class="btn" :disabled="currentPage >= totalPages" @click="goToPage(currentPage + 1)">Вперёд →</button>
        </div>
      </div>
    </div>

    <BaseModal :show="showCreateModal" @close="showCreateModal = false">
      <div class="modal-header">
        <h2 class="modal-title">Новое задание</h2>
        <p class="modal-subtitle">Создайте задание для учеников</p>
      </div>
      
      <form class="modal-form form" @submit.prevent="handleCreate">
        <div class="form-group">
          <label class="label">
            <span class="label-icon">📝</span>
            Название задания *
          </label>
          <input 
            v-model="formTitle" 
            class="input input-lg" 
            placeholder="Например, Домашняя работа №1 по алгебре" 
            required 
          />
        </div>
        
        <div class="form-group">
          <label class="label">
            <span class="label-icon">📚</span>
            Предмет
          </label>
          <input 
            v-model="formSubject" 
            class="input" 
            placeholder="Алгебра, Геометрия, Физика..." 
          />
        </div>
        
        <div class="form-group">
          <label class="label">
            <span class="label-icon">📄</span>
            Описание
          </label>
          <textarea 
            v-model="formDescription" 
            class="input textarea" 
            rows="4" 
            placeholder="Подробное описание задания, требования, рекомендации..." 
          />
        </div>
        
        <div class="form-group">
          <label class="label">
            <span class="label-icon">📎</span>
            Файлы материалов
          </label>
          <div class="file-input-wrapper">
            <input type="file" multiple @change="onFileChange" class="input" />
            <p v-if="formFiles.length > 0" class="file-hint">
              Выбрано файлов: {{ formFiles.length }}
            </p>
          </div>
        </div>
        
        <div class="modal-actions">
          <button type="button" class="btn btn-outline" @click="showCreateModal = false">
            Отмена
          </button>
          <button 
            type="submit" 
            class="btn btn-primary btn-lg" 
            :disabled="creating || !formTitle"
          >
            <span v-if="!creating">✨ Создать задание</span>
            <span v-else>⏳ Создаётся...</span>
          </button>
        </div>
      </form>
    </BaseModal>
  </div>
</template>
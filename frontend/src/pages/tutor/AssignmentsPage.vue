<!-- src/pages/tutor/AssignmentsPage.vue -->
<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { getAssignments, createAssignment, type AssignmentFilters } from '@/api/assignments'
import type { AssignmentListItem } from '@/types/assignments'
import { toApiError } from '@/api/http'
import BaseModal from '@/components/ui/BaseModal.vue'
import { listTutorStudentRelations } from '@/api/invitations'
import type { TutorStudentRelation } from '@/types/domain'

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
const isFiltering = ref(false)

// Student selection for assignment creation
const availableStudents = ref<TutorStudentRelation[]>([])
const selectedStudents = ref<number[]>([])
const studentDeadlines = ref<Record<number, string>>({})

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

const fetchAvailableStudents = async () => {
  try {
    availableStudents.value = await listTutorStudentRelations('active')
  } catch (e) {
    console.error('Failed to load students:', e)
  }
}

const handleCreate = async () => {
  if (!formTitle.value) return
  creating.value = true
  try {
    const studentsPayload = selectedStudents.value.map(studentId => ({
      student_id: studentId,
      deadline: studentDeadlines.value[studentId] || new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().slice(0, 16),
    }))
    
    await createAssignment({
      title: formTitle.value,
      description: formDescription.value || undefined,
      subject: formSubject.value || undefined,
      files: formFiles.value.length ? formFiles.value : undefined,
      students: studentsPayload.length ? studentsPayload : undefined,
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
  selectedStudents.value = []
  studentDeadlines.value = {}
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

const toggleStudent = (studentId: number) => {
  const index = selectedStudents.value.indexOf(studentId)
  if (index === -1) {
    selectedStudents.value.push(studentId)
    if (!studentDeadlines.value[studentId]) {
      studentDeadlines.value[studentId] = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().slice(0, 16)
    }
  } else {
    selectedStudents.value.splice(index, 1)
    delete studentDeadlines.value[studentId]
  }
}

const openCreateModal = async () => {
  await fetchAvailableStudents()
  showCreateModal.value = true
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
      <button class="btn btn-primary" @click="openCreateModal">+ Создать задание</button>
    </div>

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

    <!-- Create Assignment Modal -->
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
        
        <!-- Student Selection -->
        <div style="margin-top: 20px;">
          <label class="label">Выберите учеников</label>
          <div class="card" style="background: var(--bg-alt); padding: 16px; border-radius: var(--radius-md);">
            <div v-if="availableStudents.length === 0" class="muted">
              У вас пока нет активных учеников. Добавьте учеников на странице "Ученики".
            </div>
            <div v-else style="max-height: 300px; overflow-y: auto;">
              <div 
                v-for="student in availableStudents" 
                :key="student.student.id"
                class="row"
                style="align-items: center; padding: 8px 0; border-bottom: 1px solid var(--border);"
              >
                <input 
                  type="checkbox" 
                  :id="'student-' + student.student.id"
                  :checked="selectedStudents.includes(student.student.id)"
                  @change="toggleStudent(student.student.id)"
                  style="margin-right: 12px;"
                />
                <label :for="'student-' + student.student.id" style="flex: 1; cursor: pointer;">
                  {{ student.student.first_name }} {{ student.student.last_name }} ({{ student.student.email }})
                </label>
                <input 
                  v-if="selectedStudents.includes(student.student.id)"
                  v-model="studentDeadlines[student.student.id]"
                  type="datetime-local"
                  class="input"
                  style="width: 200px;"
                />
              </div>
            </div>
          </div>
          <p class="muted" style="font-size: 13px; margin-top: 8px;">
            Для каждого ученика устанавливается индивидуальный дедлайн. Выберите учеников и укажите сроки сдачи.
          </p>
        </div>
        
        <div class="row" style="justify-content: flex-end; margin-top: 20px;">
          <button type="button" class="btn" @click="showCreateModal = false">Отмена</button>
          <button type="submit" class="btn btn-primary" :disabled="creating || !formTitle || selectedStudents.length === 0">
            {{ creating ? 'Создаётся...' : 'Создать' }}
          </button>
        </div>
        <p v-if="selectedStudents.length === 0" class="muted" style="font-size: 13px; margin-top: 8px;">
          * Выберите хотя бы одного ученика для назначения задания
        </p>
      </form>
    </BaseModal>
  </div>
</template>
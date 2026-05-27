<!-- src/pages/tutor/AssignmentsPage.vue -->
<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getAssignments, createAssignment, type AssignmentFilters } from '@/api/assignments'
import type { AssignmentListItem } from '@/types/assignments'
import { toApiError } from '@/api/http'
import BaseModal from '@/components/ui/BaseModal.vue'
import {
  Search,
  Plus,
  BookOpen,
  Calendar,
  FileText,
  Paperclip,
  ChevronLeft,
  ChevronRight,
  X,
  Filter,
  Upload,
  AlignLeft
} from 'lucide-vue-next'

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

let debounceTimer: ReturnType<typeof setTimeout> | null = null

const fetchAssignments = async () => {
  loading.value = true
  errorMsg.value = ''
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

const debouncedFetch = () => {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    fetchAssignments()
  }, 350)
}

watch(
  [searchQuery, subjectFilter, deadlineBefore, deadlineAfter, statusFilter],
  () => {
    currentPage.value = 1
    debouncedFetch()
  }
)

watch(currentPage, () => {
  fetchAssignments()
})

const clearFilters = () => {
  searchQuery.value = ''
  subjectFilter.value = ''
  deadlineBefore.value = ''
  deadlineAfter.value = ''
  statusFilter.value = ''
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

const changePage = (newPage: number) => {
  if (newPage < 1 || newPage > totalPages.value) return
  currentPage.value = newPage
}

onMounted(() => {
  fetchAssignments()
})
</script>

<template>
  <div class="assignments-page">
    <!-- Заголовок -->
    <header class="page-header">
      <div>
        <h1 class="page-title">
          <BookOpen class="title-icon" :size="28" />
          Задания
        </h1>
        <p class="muted">Создавайте домашние задания и отслеживайте выполнение.</p>
      </div>
      <button class="btn btn-primary btn-create" @click="showCreateModal = true">
        <Plus :size="18" />
        Создать задание
      </button>
    </header>

    <!-- Фильтры (реальное время) -->
    <div class="filters-card">
      <div class="filters-grid">
        <div class="filter-field">
          <Search :size="16" class="field-icon" />
          <input
            v-model="searchQuery"
            class="input input-with-icon"
            placeholder="Поиск по названию..."
          />
        </div>
        <div class="filter-field">
          <BookOpen :size="16" class="field-icon" />
          <input
            v-model="subjectFilter"
            class="input input-with-icon"
            placeholder="Предмет..."
          />
        </div>
        <div class="filter-field">
          <label class="filter-label">С</label>
          <div class="input-icon-wrapper">
            <Calendar :size="16" class="field-icon" />
            <input
              v-model="deadlineAfter"
              type="date"
              class="input input-with-icon"
            />
          </div>
        </div>
        <div class="filter-field">
          <label class="filter-label">По</label>
          <div class="input-icon-wrapper">
            <Calendar :size="16" class="field-icon" />
            <input
              v-model="deadlineBefore"
              type="date"
              class="input input-with-icon"
            />
          </div>
        </div>
        <div class="filter-field">
          <Filter :size="16" class="field-icon" />
          <select v-model="statusFilter" class="input input-with-icon">
            <option value="">Все статусы</option>
            <option value="assigned">Назначено</option>
            <option value="submitted">Сдано</option>
            <option value="graded">Проверено</option>
          </select>
        </div>
        <button
          v-if="searchQuery || subjectFilter || deadlineBefore || deadlineAfter || statusFilter"
          class="btn btn-clear"
          @click="clearFilters"
        >
          <X :size="16" />
          Сбросить
        </button>
      </div>
    </div>

    <!-- Сообщения -->
    <div v-if="errorMsg" class="card error-card">
      <span class="chip chip-danger">{{ errorMsg }}</span>
    </div>
    <div v-if="loading" class="card muted card-center">
      <span>Загрузка заданий...</span>
    </div>
    <div v-else-if="assignments.length === 0" class="card card-center empty-state">
      <FileText :size="48" class="empty-icon" />
      <p class="muted">Заданий пока нет. Создайте первое.</p>
    </div>

    <!-- Таблица заданий -->
    <div v-else class="card table-card">
      <div class="card-title">
        Список заданий
        <span class="badge">{{ totalItems }}</span>
      </div>
      <div class="table-responsive">
        <table class="modern-table">
          <thead>
            <tr>
              <th><FileText :size="14" class="th-icon" /> Название</th>
              <th><BookOpen :size="14" class="th-icon" /> Предмет</th>
              <th><Calendar :size="14" class="th-icon" /> Создано</th>
              <th><Paperclip :size="14" class="th-icon" /> Файлы</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="assignment in assignments"
              :key="assignment.id"
              @click="goToDetail(assignment.id)"
              class="assignment-row"
            >
              <td class="title-cell">{{ assignment.title }}</td>
              <td>
                <span v-if="assignment.subject" class="subject-badge">
                  {{ assignment.subject }}
                </span>
                <span v-else class="muted">—</span>
              </td>
              <td class="date-cell">
                {{ new Date(assignment.created_at).toLocaleDateString('ru-RU') }}
              </td>
              <td>
                <span v-if="assignment.files_count" class="files-badge">
                  <FileText :size="14" /> {{ assignment.files_count }}
                </span>
                <span v-else class="muted">0</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Пагинация -->
      <div class="pagination-bar">
        <span class="muted">
          Страница {{ currentPage }} из {{ totalPages }}
        </span>
        <div class="pagination-buttons">
          <button
            class="btn btn-pagination"
            :disabled="currentPage <= 1"
            @click="changePage(currentPage - 1)"
          >
            <ChevronLeft :size="18" />
          </button>
          <button
            class="btn btn-pagination"
            :disabled="currentPage >= totalPages"
            @click="changePage(currentPage + 1)"
          >
            <ChevronRight :size="18" />
          </button>
        </div>
      </div>
    </div>

    <!-- Модалка создания задания -->
    <BaseModal :show="showCreateModal" @close="showCreateModal = false">
      <div class="modal-content">
        <h2 class="modal-title">Новое задание</h2>
        <form class="form" @submit.prevent="handleCreate">
          <div class="form-field">
            <label class="label">
              <FileText :size="16" class="label-icon" />
              Название *
            </label>
            <input
              v-model="formTitle"
              class="input"
              placeholder="Например, Домашняя работа №1"
              required
            />
          </div>
          <div class="form-field">
            <label class="label">
              <BookOpen :size="16" class="label-icon" />
              Предмет
            </label>
            <input
              v-model="formSubject"
              class="input"
              placeholder="Алгебра"
            />
          </div>
          <div class="form-field">
            <label class="label">
              <AlignLeft :size="16" class="label-icon" />
              Описание
            </label>
            <textarea
              v-model="formDescription"
              class="input"
              rows="3"
              placeholder="Пояснения к заданию..."
            />
          </div>
          <div class="form-field">
            <label class="label">
              <Upload :size="16" class="label-icon" />
              Файлы материалов
            </label>
            <input
              type="file"
              multiple
              @change="onFileChange"
              class="input"
            />
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-cancel" @click="showCreateModal = false">
              Отмена
            </button>
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="creating || !formTitle"
            >
              <Plus :size="18" v-if="!creating" />
              {{ creating ? 'Создаётся...' : 'Создать' }}
            </button>
          </div>
        </form>
      </div>
    </BaseModal>
  </div>
</template>

<style scoped>
/* ===== ОБЩИЕ ПЕРЕМЕННЫЕ ===== */
.assignments-page {
  --card-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
  --card-hover-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  --radius: 16px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* ===== ЗАГОЛОВОК ===== */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}
.page-title {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  color: var(--primary);
}
.title-icon {
  color: var(--primary);
}
.btn-create {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  font-weight: 600;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  transition: background 0.2s;
}
.btn-create:hover {
  background: var(--primary-600);
}

/* ===== ФИЛЬТРЫ ===== */
.filters-card {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px 20px;
  box-shadow: var(--card-shadow);
}
.filters-grid {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 12px;
}
.filter-field {
  flex: 1;
  min-width: 160px;
  display: flex;
  flex-direction: column;
}
.filter-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--muted);
  margin-bottom: 4px;
}
.input-icon-wrapper {
  position: relative;
  width: 100%;
}
.field-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--muted);
  pointer-events: none;
  z-index: 1;
}
.input-with-icon {
  padding-left: 36px !important;
}
.btn-clear {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 14px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--panel);
  color: var(--muted);
  font-weight: 500;
  transition: all 0.2s;
  white-space: nowrap;
  margin-bottom: 2px;
}
.btn-clear:hover {
  border-color: var(--primary);
  color: var(--primary);
  background: rgba(30, 58, 138, 0.05);
}

/* ===== ТАБЛИЦА ===== */
.table-card {
  padding: 0;
  overflow: hidden;
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--card-shadow);
}
.card-title {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 20px 20px 0;
  font-size: 18px;
  font-weight: 700;
}
.badge {
  background: var(--primary);
  color: white;
  border-radius: 20px;
  padding: 2px 10px;
  font-size: 13px;
  font-weight: 600;
}
.table-responsive {
  overflow-x: auto;
  margin: 0 20px;
}
.modern-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0 4px;
}
.modern-table th,
.modern-table td {
  padding: 14px 16px;
  text-align: left;
  white-space: nowrap;
}
.modern-table th {
  font-size: 13px;
  font-weight: 600;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 2px solid var(--border);
}
.th-icon {
  display: inline-block;
  vertical-align: middle;
  margin-right: 6px;
}
.assignment-row {
  cursor: pointer;
  transition: background 0.15s, box-shadow 0.15s;
}
.assignment-row:hover {
  background: rgba(30, 58, 138, 0.04);
  box-shadow: inset 4px 0 0 var(--primary);
}
.assignment-row td {
  border-bottom: 1px solid var(--border);
  font-size: 14px;
  vertical-align: middle;
}
.title-cell {
  font-weight: 600;
  color: var(--text);
}
.subject-badge {
  display: inline-block;
  background: rgba(30, 58, 138, 0.1);
  color: var(--primary);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}
.date-cell {
  color: var(--text);
}
.files-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: var(--primary);
  font-weight: 500;
}

/* ===== ПАГИНАЦИЯ ===== */
.pagination-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-top: 1px solid var(--border);
  background: var(--bg);
}
.pagination-buttons {
  display: flex;
  gap: 8px;
}
.btn-pagination {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--panel);
  color: var(--text);
  cursor: pointer;
  transition: all 0.2s;
}
.btn-pagination:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.btn-pagination:not(:disabled):hover {
  border-color: var(--primary);
  background: rgba(30, 58, 138, 0.05);
}

/* ===== СООБЩЕНИЯ ===== */
.error-card {
  background: #fef2f2;
  border-color: #fecaca;
  padding: 12px 20px;
}
.card-center {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 120px;
}
.empty-state {
  flex-direction: column;
  gap: 12px;
  padding: 40px;
  text-align: center;
}
.empty-icon {
  color: var(--muted);
  opacity: 0.5;
}

/* ===== МОДАЛЬНОЕ ОКНО ===== */
.modal-content {
  padding: 8px 4px;
}
.modal-title {
  margin: 0 0 20px;
  font-size: 22px;
  font-weight: 700;
  color: var(--primary);
  display: flex;
  align-items: center;
  gap: 10px;
}
.form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
}
.label-icon {
  color: var(--primary);
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}
.btn-cancel {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text);
}
.btn-cancel:hover {
  background: var(--bg);
}

/* ===== БАЗОВЫЕ КНОПКИ ===== */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: var(--radius-sm);
  font-weight: 600;
  transition: all 0.2s;
  cursor: pointer;
}
.btn-primary {
  background: var(--primary);
  border: 1px solid var(--primary);
  color: white;
}
.btn-primary:hover:not(:disabled) {
  background: var(--primary-600);
  border-color: var(--primary-600);
}
.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 640px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .filters-grid {
    flex-direction: column;
  }
  .filter-field {
    min-width: 100%;
  }
}
</style>
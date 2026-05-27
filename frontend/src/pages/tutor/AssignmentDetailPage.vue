<!-- src/pages/tutor/AssignmentDetailPage.vue -->
<script setup lang="ts">
import { ref, onMounted, reactive, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStudentsStore } from '@/stores/students'
import {
  getAssignmentDetail,
  updateAssignment,
  deleteAssignment,
} from '@/api/assignments'
import type { Assignment, AssignmentFile, StudentAssignment } from '@/types/assignments'
import { toApiError } from '@/api/http'

const route = useRoute()
const router = useRouter()
const studentsStore = useStudentsStore()

const assignmentId = Number(route.params.id)
const assignment = ref<Assignment | null>(null)
const loading = ref(true)
const errorMsg = ref('')
const saveMsg = ref('')

// Режим редактирования основных полей
const editMode = ref(false)
const mainForm = reactive({
  title: '',
  description: '',
  subject: '',
  max_grade: 10,
})

// Загрузка данных
const fetchAssignment = async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    assignment.value = await getAssignmentDetail(assignmentId)
    mainForm.title = assignment.value.title
    mainForm.description = assignment.value.description
    mainForm.subject = assignment.value.subject
    mainForm.max_grade = assignment.value.max_grade ?? 10
  } catch (e) {
    errorMsg.value = toApiError(e).message
  } finally {
    loading.value = false
  }
}

const fetchStudents = async () => {
  try {
    await studentsStore.loadTutorStudents('active')
  } catch (e) {
    console.error('Ошибка загрузки учеников', e)
  }
}

onMounted(async () => {
  await fetchAssignment()
  await fetchStudents()
})

// Основная информация
const toggleEditMode = () => {
  if (editMode.value) {
    if (assignment.value) {
      mainForm.title = assignment.value.title
      mainForm.description = assignment.value.description
      mainForm.subject = assignment.value.subject
      mainForm.max_grade = assignment.value.max_grade ?? 10
    }
  }
  editMode.value = !editMode.value
}

const saveMainInfo = async () => {
  if (!assignment.value) return
  loading.value = true
  saveMsg.value = ''
  try {
    const updated = await updateAssignment(assignmentId, {
      title: mainForm.title,
      description: mainForm.description,
      subject: mainForm.subject,
      max_grade: 100,
    })
    assignment.value = { ...assignment.value, ...updated }
    editMode.value = false
    saveMsg.value = '✓ Изменения сохранены'
  } catch (e) {
    alert(toApiError(e).message)
  } finally {
    loading.value = false
  }
}

// Файлы задания
const handleFileUpload = async (event: Event) => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file || !assignment.value) return
  try {
    const updated = await updateAssignment(assignmentId, { files: [file] })
    assignment.value = { ...assignment.value, ...updated }
  } catch (e) {
    alert(toApiError(e).message)
  }
}

const handleDeleteFile = async (file: AssignmentFile) => {
  if (!assignment.value) return
  const fileName = decodeURIComponent(file.file.split('/').pop() || 'файл')
  if (!confirm(`Удалить «${fileName}»?`)) return
  try {
    const updated = await updateAssignment(assignmentId, { remove_file_ids: [file.id] })
    assignment.value = { ...assignment.value, ...updated }
  } catch (e) {
    alert(toApiError(e).message)
  }
}

// Управление учениками и дедлайнами
const editingDeadlineId = ref<number | null>(null)
const editingDeadlineValue = ref('')

const startEditDeadline = (sa: StudentAssignment) => {
  editingDeadlineId.value = sa.id
  editingDeadlineValue.value = new Date(sa.deadline).toISOString().slice(0, 16)
}

const saveDeadline = async (sa: StudentAssignment) => {
  if (!assignment.value) return
  const newDeadline = new Date(editingDeadlineValue.value).toISOString()
  try {
    const updatedStudents = assignment.value.student_assignments.map(s => ({
      student_id: s.student.id,
      deadline: s.id === sa.id ? newDeadline : s.deadline,
    }))
    const updated = await updateAssignment(assignmentId, { students: updatedStudents })
    assignment.value = { ...assignment.value, ...updated }
    editingDeadlineId.value = null
  } catch (e) {
    alert(toApiError(e).message)
  }
}

const cancelEditDeadline = () => { editingDeadlineId.value = null }

const handleDeleteStudent = async (sa: StudentAssignment) => {
  if (!assignment.value) return
  const name = `${sa.student.first_name} ${sa.student.last_name}`
  if (!confirm(`Снять ученика ${name} с задания?`)) return
  const updatedStudents = assignment.value.student_assignments
    .filter(s => s.id !== sa.id)
    .map(s => ({ student_id: s.student.id, deadline: s.deadline }))
  try {
    const updated = await updateAssignment(assignmentId, { students: updatedStudents })
    assignment.value = { ...assignment.value, ...updated }
  } catch (e) {
    alert(toApiError(e).message)
  }
}

// Переход к проверке работы ученика
const handleStudentRowClick = (sa: StudentAssignment) => {
  if (sa.status === 'submitted' || sa.status === 'graded') {
    router.push(`/app/tutor/submissions/${sa.id}`)
  }
}

// Добавление учеников
const showAddStudentsModal = ref(false)
const selectedNewStudents = ref<string[]>([])
const newStudentsDeadline = ref('')

const openAddStudentsModal = () => {
  selectedNewStudents.value = []
  newStudentsDeadline.value = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
    .toISOString().slice(0, 16)
  showAddStudentsModal.value = true
}

const handleAddStudents = async () => {
  if (!assignment.value || selectedNewStudents.value.length === 0) return
  const current = assignment.value.student_assignments.map(s => ({
    student_id: s.student.id,
    deadline: s.deadline,
  }))
  const deadline = newStudentsDeadline.value
    ? new Date(newStudentsDeadline.value).toISOString()
    : new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString()
  const newItems = selectedNewStudents.value.map(id => ({
    student_id: Number(id),
    deadline,
  }))
  const allStudents = [...current, ...newItems]
  try {
    const updated = await updateAssignment(assignmentId, { students: allStudents })
    assignment.value = { ...assignment.value, ...updated }
    showAddStudentsModal.value = false
  } catch (e) {
    alert(toApiError(e).message)
  }
}

// Доступные ученики (из стора)
const availableStudents = computed(() => {
  if (!assignment.value) return []
  const assignedIds = new Set(assignment.value.student_assignments.map(s => s.student.id))
  return studentsStore.activeStudents.filter(s => !assignedIds.has(Number(s.id)))
})

// Удаление всего задания
const confirmDelete = ref(false)
const handleDeleteAssignment = async () => {
  try {
    await deleteAssignment(assignmentId)
    router.push('/app/tutor/assignments')
  } catch (e) {
    alert(toApiError(e).message)
  }
}
</script>

<template>
  <div class="assignment-page">
    <!-- Верхняя панель -->
    <header class="page-header">
      <button class="btn btn-outline" @click="router.back()">
        ← Назад к списку
      </button>
      <div class="header-actions">
        <button
          v-if="!editMode"
          class="btn btn-secondary"
          @click="toggleEditMode"
        >
          ✏️ Редактировать
        </button>
        <template v-else>
          <button
            class="btn btn-primary"
            @click="saveMainInfo"
            :disabled="loading"
          >
            💾 Сохранить
          </button>
          <button class="btn btn-outline" @click="toggleEditMode">
            Отмена
          </button>
        </template>
        <button class="btn btn-danger" @click="confirmDelete = true">
          🗑️ Удалить
        </button>
      </div>
    </header>

    <!-- Сообщения -->
    <div v-if="loading && !assignment" class="loading-state">Загрузка задания...</div>
    <div v-else-if="errorMsg" class="error-state">{{ errorMsg }}</div>
    <p v-if="saveMsg" class="success-message">{{ saveMsg }}</p>

    <template v-if="assignment">
      <div class="assignment-grid">
        <!-- Карточка основной информации -->
        <section class="card info-card">
          <div class="card-header">
            <h2 class="card-title">
              <template v-if="!editMode">{{ assignment.title }}</template>
              <input v-else v-model="mainForm.title" class="input" placeholder="Название задания" />
            </h2>
            <div class="subject-badge">
              <template v-if="!editMode">{{ assignment.subject }}</template>
              <input v-else v-model="mainForm.subject" class="input input-sm" placeholder="Предмет" />
            </div>
          </div>
          <div class="card-body">
            <div class="field">
              <label class="field-label">Описание</label>
              <p v-if="!editMode" class="description-text">{{ assignment.description || '—' }}</p>
              <textarea
                v-else
                v-model="mainForm.description"
                class="textarea"
                rows="5"
                placeholder="Подробное описание задания..."
              ></textarea>
            </div>
            <div class="field field-inline">
              <label class="field-label">Максимальный балл</label>
              <span v-if="!editMode" class="field-value">100</span>
              <input
                v-else
                v-model.number="mainForm.max_grade"
                type="number"
                class="input input-sm"
                min="1"
                max="100"
              />
            </div>
          </div>
        </section>

        <!-- Карточка материалов -->
        <section class="card files-card">
          <div class="card-header">
            <h2 class="card-title">📂 Материалы задания</h2>
          </div>
          <div class="card-body">
            <div v-if="assignment.files.length" class="file-list">
              <div
                v-for="file in assignment.files"
                :key="file.id"
                class="file-item"
              >
                <a :href="file.file" target="_blank" class="file-link">
                  <span class="file-icon">📄</span>
                  <span class="file-name">{{ decodeURIComponent(file.file.split('/').pop() || 'файл') }}</span>
                </a>
                <button
                  class="btn btn-icon-only"
                  @click="handleDeleteFile(file)"
                  title="Удалить файл"
                >
                  🗑️
                </button>
              </div>
            </div>
            <p v-else class="empty-hint">Нет прикреплённых файлов</p>
            <label class="btn btn-outline upload-label">
              <span>+ Загрузить файл</span>
              <input type="file" hidden @change="handleFileUpload" />
            </label>
          </div>
        </section>

        <!-- Карточка учеников -->
        <section class="card students-card">
          <div class="card-header">
            <h2 class="card-title">
              👨‍🎓 Ученики
              <span class="badge">{{ assignment.student_assignments.length }}</span>
            </h2>
            <button class="btn btn-secondary" @click="openAddStudentsModal">
              + Добавить
            </button>
          </div>
          <div class="card-body">
            <div v-if="assignment.student_assignments.length" class="table-responsive">
              <table class="students-table">
                <thead>
                  <tr>
                    <th>Имя</th>
                    <th>Дедлайн</th>
                    <th>Статус</th>
                    <th>Оценка</th>
                    <th>Действия</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="sa in assignment.student_assignments"
                    :key="sa.id"
                    class="student-row"
                    :class="{ 'clickable': sa.status === 'submitted' || sa.status === 'graded' }"
                    @click="handleStudentRowClick(sa)"
                  >
                    <td class="student-name">
                      {{ sa.student.first_name }} {{ sa.student.last_name }}
                    </td>
                    <td class="deadline-cell">
                      <template v-if="editingDeadlineId !== sa.id">
                        <span class="deadline-text">
                          {{ new Date(sa.deadline).toLocaleString('ru-RU') }}
                        </span>
                        <button
                          class="btn btn-icon-only"
                          @click.stop="startEditDeadline(sa)"
                          title="Изменить дедлайн"
                        >
                          ✏️
                        </button>
                      </template>
                      <template v-else>
                        <div class="deadline-edit-group">
                          <input
                            type="datetime-local"
                            v-model="editingDeadlineValue"
                            class="input input-sm"
                          />
                          <button
                            class="btn btn-icon-only"
                            @click.stop="saveDeadline(sa)"
                            title="Сохранить"
                          >
                            ✔️
                          </button>
                          <button
                            class="btn btn-icon-only"
                            @click.stop="cancelEditDeadline"
                            title="Отмена"
                          >
                            ✖️
                          </button>
                        </div>
                      </template>
                    </td>
                    <td>
                      <span
                        class="status-chip"
                        :class="'status-' + sa.status"
                      >
                        {{ sa.status === 'assigned' ? 'Назначено' :
                           sa.status === 'submitted' ? 'Сдано' :
                           sa.status === 'graded' ? 'Проверено' : sa.status }}
                      </span>
                    </td>
                    <td class="grade-cell">
                      {{ sa.grade !== null ? `${sa.grade} / ${assignment.max_grade ?? 10}` : '—' }}
                    </td>
                    <td>
                      <button
                        class="btn btn-icon-only btn-danger-icon"
                        @click.stop="handleDeleteStudent(sa)"
                        title="Снять с задания"
                      >
                        🗑️
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p v-else class="empty-hint">Ни один ученик пока не назначен</p>
          </div>
        </section>
      </div>
    </template>

    <!-- Модальное окно добавления учеников -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showAddStudentsModal" class="modal-overlay" @click.self="showAddStudentsModal = false">
          <div class="modal-content">
            <h3 class="modal-title">Добавить учеников</h3>
            <div v-if="availableStudents.length" class="student-select-list">
              <label
                v-for="s in availableStudents"
                :key="s.id"
                class="student-select-item"
              >
                <input
                  type="checkbox"
                  :value="s.id"
                  v-model="selectedNewStudents"
                  class="checkbox"
                />
                <span>{{ s.name }}</span>
                <span class="student-email">{{ s.email }}</span>
              </label>
            </div>
            <p v-else class="empty-hint">Все активные ученики уже назначены</p>
            <div class="form-group">
              <label class="form-label">Общий дедлайн</label>
              <input
                type="datetime-local"
                v-model="newStudentsDeadline"
                class="input"
              />
            </div>
            <div class="modal-actions">
              <button class="btn btn-outline" @click="showAddStudentsModal = false">
                Отмена
              </button>
              <button
                class="btn btn-primary"
                @click="handleAddStudents"
                :disabled="selectedNewStudents.length === 0"
              >
                Добавить выбранных
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Модальное окно подтверждения удаления -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="confirmDelete" class="modal-overlay" @click.self="confirmDelete = false">
          <div class="modal-content modal-confirm">
            <h3 class="modal-title">Удалить задание?</h3>
            <p class="confirm-text">
              Вы действительно хотите полностью удалить «{{ assignment?.title }}»?
              Все файлы, ответы и оценки будут потеряны.
            </p>
            <div class="modal-actions">
              <button class="btn btn-outline" @click="confirmDelete = false">
                Отмена
              </button>
              <button class="btn btn-danger" @click="handleDeleteAssignment">
                Да, удалить
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>

.assignment-page {
  max-width: 1100px;
  margin: 0 auto;
  padding: 20px 16px 40px;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  color: var(--text);
}

/* ----- Шапка ----- */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 24px;
}

.header-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

/* ----- Сетка карточек ----- */
.assignment-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
}

@media (min-width: 768px) {
  .assignment-grid {
    grid-template-columns: 1fr 1fr;
    grid-template-rows: auto auto;
  }
  .info-card {
    grid-column: 1 / -1;
  }
}

/* ----- Карточки ----- */
.card {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md, 0 4px 12px rgba(0,0,0,0.06));
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.card-header {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.card-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.card-title input {
  font-size: inherit;
  font-weight: inherit;
  width: 100%;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 6px 10px;
}

.card-body {
  padding: 20px;
  flex: 1;
}

.subject-badge {
  background: rgba(37, 99, 235, 0.08);
  color: var(--primary);
  border-radius: 20px;
  padding: 4px 12px;
  font-size: 0.85rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
}

.subject-badge input {
  border: none;
  background: transparent;
  font-weight: 600;
  color: var(--primary);
  outline: none;
  width: auto;
  min-width: 80px;
}

/* Поля */
.field {
  margin-bottom: 16px;
}

.field-inline {
  display: flex;
  align-items: center;
  gap: 12px;
}

.field-label {
  font-weight: 600;
  font-size: 0.85rem;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 4px;
  display: block;
}

.field-inline .field-label {
  margin-bottom: 0;
}

.field-value {
  font-weight: 500;
}

.description-text {
  white-space: pre-wrap;
  line-height: 1.6;
  margin: 0;
}

/* ----- Кнопки ----- */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 16px;
  border: 1px solid transparent;
  border-radius: var(--radius-sm);
  font-weight: 500;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s, color 0.2s;
  white-space: nowrap;
}

.btn-primary {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
}
.btn-primary:hover { background: #1d4ed8; }

.btn-secondary {
  background: #f0f0f0;
  color: var(--text);
  border-color: var(--border);
}
.btn-secondary:hover { background: #e0e0e0; }

.btn-outline {
  background: transparent;
  border-color: var(--border);
  color: var(--text);
}
.btn-outline:hover { background: #f9fafb; }

.btn-danger {
  background: var(--danger);
  color: white;
  border-color: var(--danger);
}
.btn-danger:hover { background: #b91c1c; }

.btn-icon-only {
  padding: 6px 8px;
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  border-radius: var(--radius-sm);
  color: var(--muted);
  transition: background 0.2s, color 0.2s;
}
.btn-icon-only:hover {
  background: rgba(0,0,0,0.06);
  color: var(--text);
}

.btn-danger-icon:hover {
  background: rgba(220, 38, 38, 0.1);
  color: var(--danger);
}

/* ----- Файлы ----- */
.file-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  transition: border-color 0.2s;
}
.file-item:hover {
  border-color: var(--primary);
}

.file-link {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  color: var(--text);
  flex: 1;
  overflow: hidden;
}

.file-icon {
  font-size: 1.2rem;
}

.file-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.upload-label {
  cursor: pointer;
  display: inline-flex;
}

/* ----- Таблица учеников ----- */
.table-responsive {
  overflow-x: auto;
  margin: -8px -20px 0;
  padding: 0 20px;
}

.students-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.students-table th {
  text-align: left;
  padding: 12px 8px;
  border-bottom: 2px solid var(--border);
  color: var(--muted);
  font-weight: 600;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.students-table td {
  padding: 10px 8px;
  border-bottom: 1px solid var(--border);
  vertical-align: middle;
}

.student-row:last-child td {
  border-bottom: none;
}

.student-row.clickable {
  cursor: pointer;
  transition: background-color 0.2s;
}

.student-row.clickable:hover {
  background-color: #f0f7ff;
}

.deadline-cell {
  min-width: 180px;
}

.deadline-text {
  margin-right: 8px;
  font-size: 0.85rem;
}

.deadline-edit-group {
  display: flex;
  align-items: center;
  gap: 4px;
}

.status-chip {
  display: inline-block;
  padding: 2px 12px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-assigned { background: #e2e8f0; color: #334155; }
.status-submitted { background: #fef3c7; color: #92400e; }
.status-graded { background: #d1fae5; color: #065f46; }

.grade-cell {
  font-weight: 500;
}

.badge {
  background: var(--primary);
  color: white;
  border-radius: 20px;
  padding: 2px 10px;
  font-size: 0.8rem;
  font-weight: 600;
}

/* Модальные окна */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: var(--panel);
  border-radius: var(--radius-lg);
  padding: 24px;
  width: 90%;
  max-width: 520px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25);
}

.modal-title {
  margin: 0 0 20px;
  font-size: 1.25rem;
  font-weight: 700;
}

.confirm-text {
  color: var(--muted);
  line-height: 1.5;
  margin-bottom: 24px;
}

.student-select-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
  max-height: 200px;
  overflow-y: auto;
}

.student-select-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  border-radius: var(--radius-sm);
  transition: background 0.2s;
  cursor: pointer;
}

.student-select-item:hover {
  background: var(--bg);
}

.student-email {
  font-size: 0.8rem;
  color: var(--muted);
  margin-left: auto;
}

.checkbox {
  width: 18px;
  height: 18px;
  accent-color: var(--primary);
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  font-size: 0.9rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* Переходы */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}
.modal-enter-active .modal-content,
.modal-leave-active .modal-content {
  transition: transform 0.2s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
.modal-enter-from .modal-content {
  transform: scale(0.95);
}
.modal-leave-to .modal-content {
  transform: scale(0.95);
}

/* Сообщения */
.success-message {
  background: #d1fae5;
  color: #065f46;
  padding: 12px 16px;
  border-radius: var(--radius-sm);
  margin-bottom: 20px;
  font-weight: 500;
}

.loading-state,
.error-state {
  text-align: center;
  padding: 40px 20px;
  font-size: 1.1rem;
  color: var(--muted);
}

.error-state {
  color: var(--danger);
}

.empty-hint {
  color: var(--muted);
  font-style: italic;
  margin: 8px 0;
}
</style>
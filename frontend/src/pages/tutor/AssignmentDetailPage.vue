<!-- src/pages/tutor/AssignmentDetailPage.vue -->
<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  getAssignmentDetail,
  uploadAssignmentFile,
  assignStudentsToAssignment,
  gradeAssignment,
} from '@/api/assignments'
import { http, toApiError } from '@/api/http'
import type { Assignment, StudentAssignment } from '@/types/assignments'
import BaseModal from '@/components/ui/BaseModal.vue'

const route = useRoute()
const router = useRouter()
const id = Number(route.params.id)
const assignment = ref<Assignment | null>(null)
const loading = ref(false)
const errorMsg = ref('')

// Назначение студентов
const showAssignModal = ref(false)
const allStudents = ref<{ student_id: number; name: string; email: string }[]>([])
const selectedStudents = ref<{ student_id: number; name: string; deadline: string }[]>([])
const defaultDeadline = ref('')
const assigning = ref(false)

// Оценивание
const selectedStudentAssignment = ref<StudentAssignment | null>(null)
const gradeValue = ref<number | null>(null)
const gradeComment = ref('')
const grading = ref(false)

const fetchAssignment = async () => {
  loading.value = true
  try {
    assignment.value = await getAssignmentDetail(id)
  } catch (e) {
    errorMsg.value = toApiError(e).message
  } finally {
    loading.value = false
  }
}

const handleFileUpload = async (e: Event) => {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  try {
    await uploadAssignmentFile(id, file)
    await fetchAssignment()
  } catch (e) {
    alert(toApiError(e).message)
  }
}

// Загрузка списка активных учеников
const loadStudents = async () => {
  try {
    const { data } = await http.get('/v1/tutor-students/')
    // data — массив TutorStudent, фильтруем по active
    allStudents.value = (data as any[])
      .filter((rel: any) => rel.status === 'active')
      .map((rel: any) => ({
        student_id: rel.student.id,
        name: `${rel.student.first_name} ${rel.student.last_name}`,
        email: rel.student.email,
      }))
  } catch (e) {
    alert('Не удалось загрузить список учеников')
  }
}

// Открыть модалку и загрузить учеников
watch(showAssignModal, (newVal) => {
  if (newVal) {
    loadStudents()
    // Инициализируем выбранных из уже назначенных (если есть)
    if (assignment.value) {
      selectedStudents.value = assignment.value.student_assignments.map(sa => ({
        student_id: sa.student.id,
        name: `${sa.student.first_name} ${sa.student.last_name}`,
        deadline: sa.deadline,
      }))
    }
  }
})

const addStudent = (student: { student_id: number; name: string }) => {
  if (!selectedStudents.value.find(s => s.student_id === student.student_id)) {
    selectedStudents.value.push({
      student_id: student.student_id,
      name: student.name,
      deadline: defaultDeadline.value || new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().slice(0, 16),
    })
  }
}

const removeStudent = (studentId: number) => {
  selectedStudents.value = selectedStudents.value.filter(s => s.student_id !== studentId)
}

const updateStudentDeadline = (studentId: number, deadline: string) => {
  const student = selectedStudents.value.find(s => s.student_id === studentId)
  if (student) student.deadline = deadline
}

const handleAssignStudents = async () => {
  if (!selectedStudents.value.length) return
  assigning.value = true
  try {
    await assignStudentsToAssignment(id, {
      assignments_data: selectedStudents.value.map(s => ({
        student_id: s.student_id,
        deadline: new Date(s.deadline).toISOString(),
      })),
    })
    showAssignModal.value = false
    await fetchAssignment()
  } catch (e) {
    alert(toApiError(e).message)
  } finally {
    assigning.value = false
  }
}

const openGradeModal = (sa: StudentAssignment) => {
  selectedStudentAssignment.value = sa
  gradeValue.value = sa.grade ?? null
  gradeComment.value = sa.tutor_comment ?? ''
}

const handleGrade = async () => {
  if (!selectedStudentAssignment.value || gradeValue.value == null) return
  grading.value = true
  try {
    await gradeAssignment(selectedStudentAssignment.value.id, gradeValue.value, gradeComment.value)
    selectedStudentAssignment.value = null
    await fetchAssignment()
  } catch (e) {
    alert(toApiError(e).message)
  } finally {
    grading.value = false
  }
}

const statusChipClass = (status: string) => {
  switch (status) {
    case 'graded': return 'chip-success'
    case 'submitted': return 'chip-warning'
    default: return ''
  }
}

onMounted(fetchAssignment)
</script>

<template>
  <div class="page assignments-detail">
    <button class="btn back-btn" @click="router.push('/app/tutor/assignments')">← Назад к списку</button>

    <div v-if="loading" class="muted loading-msg">Загрузка...</div>
    <div v-else-if="errorMsg" class="chip chip-danger error-chip">{{ errorMsg }}</div>

    <template v-if="assignment">
      <div class="header-card card">
        <div class="header-title">
          <h1 class="page-title">{{ assignment.title }}</h1>
          <span class="subject-badge">{{ assignment.subject || 'Без предмета' }}</span>
        </div>
        <p class="muted creation-date">Создано {{ new Date(assignment.created_at).toLocaleDateString() }}</p>
      </div>

      <div class="card description-card">
        <h3 class="card-title">Описание</h3>
        <div class="description-text">{{ assignment.description || 'Нет описания' }}</div>
      </div>

      <div class="card files-card">
        <div class="card-title-row">
          <h3 class="card-title">📎 Файлы задания</h3>
          <label class="btn btn-outline upload-btn">
            + Загрузить
            <input type="file" hidden @change="handleFileUpload" />
          </label>
        </div>
        <ul v-if="assignment.files.length" class="file-list">
          <li v-for="f in assignment.files" :key="f.id">
            <a :href="f.file" target="_blank">{{ f.file.split('/').pop() }}</a>
            <span class="muted"> ({{ new Date(f.uploaded_at).toLocaleDateString() }})</span>
          </li>
        </ul>
        <p v-else class="muted">Файлов пока нет</p>
      </div>

      <div class="card students-card">
        <div class="card-title-row">
          <h3 class="card-title">👥 Назначенные ученики</h3>
          <button class="btn btn-primary" @click="showAssignModal = true">+ Назначить</button>
        </div>
        <div v-if="assignment.student_assignments.length === 0" class="muted">Никто не назначен</div>
        <div v-else class="table-wrapper">
          <table class="table">
            <thead>
              <tr><th>Ученик</th><th>Дедлайн</th><th>Статус</th><th>Оценка</th><th></th></tr>
            </thead>
            <tbody>
              <tr v-for="sa in assignment.student_assignments" :key="sa.id">
                <td>{{ sa.student.first_name }} {{ sa.student.last_name }}</td>
                <td>{{ new Date(sa.deadline).toLocaleString() }}</td>
                <td><span class="chip" :class="statusChipClass(sa.status)">{{ sa.status }}</span></td>
                <td>{{ sa.grade ?? '—' }}</td>
                <td>
                  <button v-if="sa.status === 'submitted'" class="btn btn-primary btn-sm" @click="openGradeModal(sa)">
                    Проверить
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>

    <!-- Модальное окно назначения учеников -->
    <BaseModal :show="showAssignModal" @close="showAssignModal = false">
      <div class="assign-modal">
        <h2>Назначить учеников</h2>
        <p class="muted">Выберите учеников и установите сроки</p>

        <div class="students-grid">
          <div
            v-for="student in allStudents"
            :key="student.student_id"
            class="student-chip"
            :class="{ 'selected': selectedStudents.some(s => s.student_id === student.student_id) }"
          >
            <span class="student-name">{{ student.name }}</span>
            <span class="student-email muted">{{ student.email }}</span>
            <div class="chip-actions">
              <button
                v-if="!selectedStudents.some(s => s.student_id === student.student_id)"
                class="btn btn-icon btn-plus"
                @click="addStudent(student)"
                title="Добавить"
              >+</button>
              <button
                v-else
                class="btn btn-icon btn-minus"
                @click="removeStudent(student.student_id)"
                title="Убрать"
              >−</button>
            </div>
          </div>
        </div>

        <div v-if="selectedStudents.length > 0" class="selected-section">
          <h3>Выбрано ({{ selectedStudents.length }})</h3>
          <div class="selected-list">
            <div v-for="s in selectedStudents" :key="s.student_id" class="selected-item">
              <span class="selected-name">{{ s.name }}</span>
              <input
                type="datetime-local"
                class="input deadline-input"
                :value="s.deadline"
                @change="updateStudentDeadline(s.student_id, ($event.target as HTMLInputElement).value)"
              />
              <button class="btn btn-icon btn-remove" @click="removeStudent(s.student_id)" title="Удалить">✕</button>
            </div>
          </div>
          <div class="default-deadline">
            <label class="label">Дедлайн по умолчанию для новых:</label>
            <input type="datetime-local" v-model="defaultDeadline" class="input" />
          </div>
        </div>

        <div class="modal-actions">
          <button class="btn" @click="showAssignModal = false">Отмена</button>
          <button
            class="btn btn-primary"
            :disabled="assigning || !selectedStudents.length"
            @click="handleAssignStudents"
          >
            {{ assigning ? 'Сохранение...' : 'Назначить' }}
          </button>
        </div>
      </div>
    </BaseModal>

    <!-- Модальное окно оценивания -->
    <BaseModal :show="!!selectedStudentAssignment" @close="selectedStudentAssignment = null">
      <template v-if="selectedStudentAssignment">
        <h2>Оценить работу {{ selectedStudentAssignment.student.first_name }}</h2>
        <form class="form" @submit.prevent="handleGrade">
          <label class="label">Оценка (0-100)</label>
          <input v-model.number="gradeValue" type="number" min="0" max="100" class="input" />
          <label class="label">Комментарий</label>
          <textarea v-model="gradeComment" class="input" rows="3"></textarea>
          <div class="row" style="justify-content: flex-end;">
            <button type="button" class="btn" @click="selectedStudentAssignment = null">Отмена</button>
            <button type="submit" class="btn btn-primary" :disabled="grading || gradeValue == null">Выставить оценку</button>
          </div>
        </form>
      </template>
    </BaseModal>
  </div>
</template>

<style scoped>
/* Общие улучшения для страницы */
.assignments-detail {
  max-width: 900px;
  margin: 0 auto;
}

.back-btn {
  align-self: flex-start;
  margin-bottom: 8px;
  color: var(--primary);
  border: none;
  background: none;
  font-weight: 600;
}
.back-btn:hover {
  text-decoration: underline;
}

.header-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
}
.header-title {
  display: flex;
  align-items: baseline;
  gap: 12px;
}
.subject-badge {
  background: var(--primary);
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}
.creation-date {
  font-size: 14px;
  white-space: nowrap;
}

.card-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.file-list {
  list-style: none;
  padding: 0;
  margin: 8px 0 0;
}
.file-list li {
  padding: 6px 0;
  display: flex;
  align-items: center;
  gap: 6px;
}

.table-wrapper {
  overflow-x: auto;
}

/* Кнопки */
.btn-sm {
  padding: 6px 10px;
  font-size: 13px;
}
.btn-outline {
  border: 1px solid var(--primary);
  color: var(--primary);
  background: transparent;
  cursor: pointer;
}
.btn-outline:hover {
  background: rgba(30, 58, 138, 0.05);
}
.btn-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 20px;
  border: none;
  cursor: pointer;
  background: transparent;
  transition: background 0.2s;
}
.btn-plus:hover {
  background: rgba(16, 185, 129, 0.15);
  color: var(--success);
}
.btn-minus:hover {
  background: rgba(239, 68, 68, 0.15);
  color: var(--danger);
}
.btn-remove {
  font-size: 16px;
}
.btn-remove:hover {
  background: rgba(239, 68, 68, 0.15);
  color: var(--danger);
}

/* Модалка назначения */
.assign-modal {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.students-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  max-height: 300px;
  overflow-y: auto;
  padding: 4px 0;
}

.student-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border: 1px solid var(--border);
  border-radius: 24px;
  background: var(--panel);
  transition: all 0.2s;
}
.student-chip.selected {
  border-color: var(--primary);
  background: rgba(30, 58, 138, 0.05);
}
.student-name {
  font-weight: 600;
}
.student-email {
  font-size: 12px;
}
.chip-actions {
  margin-left: 4px;
}

.selected-section {
  border-top: 1px solid var(--border);
  padding-top: 12px;
}
.selected-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 8px 0;
}
.selected-item {
  display: flex;
  align-items: center;
  gap: 12px;
}
.selected-name {
  min-width: 120px;
  font-weight: 500;
}
.deadline-input {
  flex: 1;
  padding: 8px;
  font-size: 14px;
}
.default-deadline {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 8px;
}
.default-deadline .label {
  margin-bottom: 0;
  white-space: nowrap;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 8px;
}

.error-chip {
  margin-bottom: 12px;
}
.loading-msg {
  text-align: center;
  padding: 20px;
}
</style>
<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useStudentsStore } from '../../stores/students'
import type { StudentGroupType, Student } from '../../types/domain'

const students = useStudentsStore()

onMounted(() => {
  // In MVP data is seeded at login, but keep it robust if user refreshes.
  if (students.getAll.length === 0) students.seedForRole('tutor')
})

const privateStudents = computed(() => students.getByGroup('private'))
const groupStudents = computed(() => students.getByGroup('group'))

const isModalOpen = ref(false)
const modalMode = ref<'create' | 'edit'>('create')
const form = ref<{
  id?: string
  name: string
  email: string
  subject: string
  groupType: StudentGroupType
}>({
  name: '',
  email: '',
  subject: '',
  groupType: 'private',
})

function openCreate(groupType: StudentGroupType) {
  modalMode.value = 'create'
  form.value = { name: '', email: '', subject: '', groupType }
  isModalOpen.value = true
}

function openEdit(student: Student) {
  modalMode.value = 'edit'
  form.value = {
    id: student.id,
    name: student.name,
    email: student.email,
    subject: student.subject,
    groupType: student.groupType,
  }
  isModalOpen.value = true
}

function closeModal() {
  isModalOpen.value = false
}

function submit() {
  const name = form.value.name.trim()
  const email = form.value.email.trim()
  const subject = form.value.subject.trim()
  if (!name || !email || !subject) return

  if (modalMode.value === 'create') {
    students.createStudent({
      name,
      email,
      subject,
      groupType: form.value.groupType,
    })
  } else if (modalMode.value === 'edit' && form.value.id) {
    students.updateStudent(form.value.id, {
      name,
      email,
      subject,
      groupType: form.value.groupType,
    })
  }

  closeModal()
}

function removeStudent(student: Student) {
  // API (later):
  // await deleteStudentApi(student.id)
  students.deleteStudent(student.id)
}

function groupTitle(group: StudentGroupType) {
  return group === 'private' ? 'Индивидуальные занятия' : 'Групповые занятия'
}
</script>

<template>
  <div class="page">
    <div>
      <h1 class="page-title">Ученики</h1>
      <p class="muted" style="margin: 8px 0 0 0;">
        Разделяйте учеников по типу занятий и управляйте списком.
      </p>
    </div>

    <div class="grid grid-cols-2">
      <div class="card">
        <div class="row">
          <div>
            <div class="card-title">Индивидуальные занятия</div>
            <div class="muted">{{ privateStudents.length }} учеников</div>
          </div>
          <button class="btn btn-primary" type="button" @click="openCreate('private')">
            Добавить
          </button>
        </div>

        <div style="overflow-x: auto; margin-top: 12px;">
          <table class="table">
            <thead>
              <tr>
                <th>Имя</th>
                <th>Email</th>
                <th>Предмет</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="s in privateStudents" :key="s.id">
                <td>{{ s.name }}</td>
                <td>{{ s.email }}</td>
                <td>{{ s.subject }}</td>
                <td style="white-space: nowrap;">
                  <button class="btn" type="button" @click="openEdit(s)">Изменить</button>
                  <button class="btn" type="button" @click="removeStudent(s)">Удалить</button>
                </td>
              </tr>
              <tr v-if="privateStudents.length === 0">
                <td colspan="4" class="muted">Нет учеников</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="card">
        <div class="row">
          <div>
            <div class="card-title">Групповые занятия</div>
            <div class="muted">{{ groupStudents.length }} учеников</div>
          </div>
          <button class="btn btn-primary" type="button" @click="openCreate('group')">
            Добавить
          </button>
        </div>

        <div style="overflow-x: auto; margin-top: 12px;">
          <table class="table">
            <thead>
              <tr>
                <th>Имя</th>
                <th>Email</th>
                <th>Предмет</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="s in groupStudents" :key="s.id">
                <td>{{ s.name }}</td>
                <td>{{ s.email }}</td>
                <td>{{ s.subject }}</td>
                <td style="white-space: nowrap;">
                  <button class="btn" type="button" @click="openEdit(s)">Изменить</button>
                  <button class="btn" type="button" @click="removeStudent(s)">Удалить</button>
                </td>
              </tr>
              <tr v-if="groupStudents.length === 0">
                <td colspan="4" class="muted">Нет учеников</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div v-if="isModalOpen" class="modal-backdrop" @click="closeModal" />
    <div
      v-if="isModalOpen"
      class="modal"
      role="dialog"
      aria-modal="true"
      aria-label="Управление учеником"
    >
      <div class="modal-header">
        <div>
          <div class="card-title" style="font-size: 18px;">
            {{ modalMode === 'create' ? 'Добавить ученика' : 'Изменить ученика' }}
          </div>
          <div class="muted" style="margin-top: 4px;">
            {{ groupTitle(form.groupType) }}
          </div>
        </div>
        <button class="btn" type="button" @click="closeModal">Закрыть</button>
      </div>

      <div class="form" style="margin-top: 12px;">
        <div>
          <div class="label">Имя</div>
          <input v-model="form.name" class="input" type="text" placeholder="Имя" />
        </div>
        <div>
          <div class="label">Email</div>
          <input v-model="form.email" class="input" type="email" placeholder="name@example.com" />
        </div>
        <div>
          <div class="label">Предмет</div>
          <input v-model="form.subject" class="input" type="text" placeholder="Алгебра" />
        </div>

        <div>
          <div class="label">Тип занятий</div>
          <div class="grid grid-cols-2">
            <button
              type="button"
              class="btn"
              :style="form.groupType === 'private' ? { borderColor: 'rgba(30, 58, 138, 0.6)' } : undefined"
              @click="form.groupType = 'private'"
            >
              Индивидуальные
            </button>
            <button
              type="button"
              class="btn"
              :style="form.groupType === 'group' ? { borderColor: 'rgba(30, 58, 138, 0.6)' } : undefined"
              @click="form.groupType = 'group'"
            >
              Групповые
            </button>
          </div>
        </div>

        <div class="row" style="margin-top: 6px;">
          <button class="btn" type="button" @click="closeModal">
            Отмена
          </button>
          <button class="btn btn-primary" type="button" @click="submit" :disabled="!form.name.trim() || !form.email.trim() || !form.subject.trim()">
            Сохранить
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.35);
  z-index: 20;
}

.modal {
  position: fixed;
  top: 84px;
  left: 50%;
  transform: translateX(-50%);
  width: min(720px, calc(100vw - 24px));
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 14px;
  z-index: 21;
}

.modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}
</style>


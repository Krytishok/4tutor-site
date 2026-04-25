<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import WeekCalendar from '../../components/calendar/WeekCalendar.vue'
import { useScheduleStore } from '../../stores/schedule'
import { useStudentsStore } from '../../stores/students'
import type { ScheduleEvent } from '../../types/domain'
import { toApiError } from '../../api/http'

const schedule = useScheduleStore()
const students = useStudentsStore()
const apiError = ref('')
const deleteConfirmOpen = ref(false)

onMounted(() => {
  void Promise.all([students.loadTutorStudents('active'), schedule.loadEvents()])
})

const events = computed(() => schedule.getEvents)
const studentsById = computed<Record<string, string>>(() => {
  const map: Record<string, string> = {}
  for (const s of students.getAll) map[s.id] = s.name
  return map
})

const selectedEvent = ref<ScheduleEvent | null>(null)
const isDetailsOpen = ref(false)
const formMode = ref<'create' | 'edit'>('create')
const isFormOpen = ref(false)
const form = ref({
  subject: '',
  startDate: new Date().toISOString().slice(0, 10),
  startTime: '18:00',
  durationMins: 60,
  studentIds: [] as string[],
  meetingUrl: '',
  isRecurringWeekly: false,
})

const durationOptions = [30, 45, 60, 75, 90, 120]
const activeStudents = computed(() => students.getAll)

// Проверка пересечений занятий
function hasTimeConflict(start: Date, end: Date, excludeEventId?: string): boolean {
  const existing = schedule.getEvents.filter(e => e.id !== excludeEventId)
  return existing.some(ev => {
    const evStart = new Date(ev.startAt)
    const evEnd = new Date(ev.endAt)
    return start < evEnd && end > evStart
  })
}

// Переключение ученика в форме
function toggleStudent(id: string) {
  const idx = form.value.studentIds.indexOf(id)
  if (idx === -1) {
    form.value.studentIds.push(id)
  } else {
    form.value.studentIds.splice(idx, 1)
  }
}

function openCreate() {
  formMode.value = 'create'
  form.value.subject = ''
  form.value.startDate = new Date().toISOString().slice(0, 10)
  form.value.startTime = '18:00'
  form.value.durationMins = 60
  form.value.studentIds = activeStudents.value.slice(0, 1).map((s) => s.id)
  form.value.meetingUrl = ''
  form.value.isRecurringWeekly = false
  isFormOpen.value = true
  isDetailsOpen.value = false
}

function openEdit(ev: ScheduleEvent) {
  // Не открываем форму для фиктивных повторений
  if (ev.id.includes('_')) return
  formMode.value = 'edit'
  form.value.subject = ev.subject
  const start = new Date(ev.startAt)
  const end = new Date(ev.endAt)
  form.value.startDate = start.toISOString().slice(0, 10)
  form.value.startTime = `${String(start.getHours()).padStart(2, '0')}:${String(start.getMinutes()).padStart(2, '0')}`
  form.value.durationMins = Math.max(30, Math.round((end.getTime() - start.getTime()) / 60000))
  form.value.studentIds = ev.studentIds
  form.value.meetingUrl = ev.meetingUrl ?? ''
  form.value.isRecurringWeekly = Boolean(ev.isRecurringWeekly)
  selectedEvent.value = ev
  isFormOpen.value = true
  isDetailsOpen.value = false
}

function closeForm() {
  isFormOpen.value = false
}

function closeDetails() {
  isDetailsOpen.value = false
  selectedEvent.value = null
  deleteConfirmOpen.value = false
}

function formatTime(iso: string) {
  return new Date(iso).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit', weekday: 'long' })
}

function buildLocalDateTime(dateStr: string, timeStr: string) {
  const [yRaw, mRaw, dRaw] = dateStr.split('-').map((x) => Number(x))
  const [hhRaw, mmRaw] = timeStr.split(':').map((x) => Number(x))
  const y = yRaw ?? new Date().getFullYear()
  const m = mRaw ?? 1
  const d = dRaw ?? 1
  const hh = hhRaw ?? 0
  const mm = mmRaw ?? 0
  return new Date(y, m - 1, d, hh, mm, 0, 0)
}

function selectedStudentNames(ev: ScheduleEvent) {
  return ev.studentIds.map((id) => studentsById.value[id] ?? `ID ${id}`)
}

async function submitForm() {
  apiError.value = ''
  const subject = form.value.subject.trim()
  if (!subject || form.value.studentIds.length === 0) return

  const start = buildLocalDateTime(form.value.startDate, form.value.startTime)
  const end = new Date(start.getTime() + form.value.durationMins * 60000)

  // Проверка пересечений
  const excludeId = formMode.value === 'edit' ? selectedEvent.value?.id : undefined
  if (hasTimeConflict(start, end, excludeId)) {
    apiError.value = 'Это время пересекается с другим занятием.'
    return
  }

  const payload = {
    groupType: form.value.studentIds.length > 1 ? 'group' : 'private',
    subject,
    startAt: start.toISOString(),
    endAt: end.toISOString(),
    studentIds: form.value.studentIds,
    meetingUrl: form.value.meetingUrl.trim() || undefined,
    isRecurringWeekly: form.value.isRecurringWeekly,
  } satisfies Omit<ScheduleEvent, 'id'>

  try {
    if (formMode.value === 'create') {
      await schedule.createEvent(payload)
    } else if (selectedEvent.value) {
      await schedule.updateEvent(selectedEvent.value.id, payload)
    }
    closeForm()
    closeDetails()
  } catch (err) {
    apiError.value = toApiError(err).message
  }
}

function onSelectEvent(ev: ScheduleEvent) {
  selectedEvent.value = ev
  isDetailsOpen.value = true
}

async function confirmDelete() {
  if (!selectedEvent.value) return
  // Не удаляем фиктивные повторения
  if (selectedEvent.value.id.includes('_')) return
  try {
    await schedule.deleteEvent(selectedEvent.value.id)
    closeDetails()
  } catch (err) {
    apiError.value = toApiError(err).message
  }
}
</script>

<template>
  <div class="page">
    <div>
      <h1 class="page-title">Расписание</h1>
      <p class="muted" style="margin: 8px 0 0 0;">Уроки за неделю (понедельник-воскресенье).</p>
    </div>

    <div class="card schedule-card">
      <div class="row" style="margin-bottom: 12px;">
        <div>
          <div class="card-title" style="margin-bottom: 4px;">Неделя</div>
          <div class="muted">Полный обзор недели и быстрый доступ к деталям урока.</div>
        </div>
        <button class="btn btn-primary" type="button" @click="openCreate">Добавить занятие</button>
      </div>

      <WeekCalendar :events="events" :students-by-id="studentsById" @select="onSelectEvent" />
    </div>

    <div v-if="isDetailsOpen && selectedEvent" class="modal-backdrop" @click="closeDetails" />
    <div v-if="isDetailsOpen && selectedEvent" class="modal" role="dialog" aria-modal="true">
      <div class="modal-header">
        <div>
          <div class="card-title" style="font-size: 20px;">{{ selectedEvent.subject }}</div>
          <div class="muted" style="margin-top: 4px;">
            {{ `${formatDate(selectedEvent.startAt)} • ${formatTime(selectedEvent.startAt)}–${formatTime(selectedEvent.endAt)}` }}
          </div>
        </div>
        <button class="btn" type="button" @click="closeDetails">Закрыть</button>
      </div>

      <div class="details-grid">
        <div class="detail-item">
          <div class="muted">Тип</div>
          <div>{{ selectedEvent.groupType === 'group' ? 'Групповое' : 'Индивидуальное' }}</div>
        </div>
        <div class="detail-item">
          <div class="muted">Повторение</div>
          <div>{{ selectedEvent.isRecurringWeekly ? 'Каждую неделю' : 'Разовое' }}</div>
        </div>
        <div class="detail-item" style="grid-column: 1 / -1;">
          <div class="muted">Ученики</div>
          <div class="chips-row">
            <span v-for="name in selectedStudentNames(selectedEvent)" :key="name" class="chip">{{ name }}</span>
          </div>
        </div>
        <div class="detail-item" v-if="selectedEvent.meetingUrl" style="grid-column: 1 / -1;">
          <div class="muted">Ссылка</div>
          <a :href="selectedEvent.meetingUrl" target="_blank" rel="noreferrer">{{ selectedEvent.meetingUrl }}</a>
        </div>
      </div>

      <div class="row" style="margin-top: 12px;">
        <button
          v-if="!selectedEvent.id.includes('_')"
          class="btn"
          type="button"
          @click="openEdit(selectedEvent)"
        >
          Изменить
        </button>
        <button
          v-if="!selectedEvent.id.includes('_')"
          class="btn btn-danger"
          type="button"
          @click="deleteConfirmOpen = true"
        >
          Удалить
        </button>
      </div>

      <div v-if="deleteConfirmOpen" class="confirm-box">
        <div>Удалить занятие? Это действие нельзя отменить.</div>
        <div class="row" style="margin-top: 10px;">
          <button class="btn" type="button" @click="deleteConfirmOpen = false">Отмена</button>
          <button class="btn btn-danger" type="button" @click="confirmDelete">Подтвердить удаление</button>
        </div>
      </div>
    </div>

    <div v-if="isFormOpen" class="modal-backdrop" @click="closeForm" />
    <div v-if="isFormOpen" class="modal" role="dialog" aria-modal="true">
      <div class="modal-header">
        <div>
          <div class="card-title" style="font-size: 18px;">
            {{ formMode === 'create' ? 'Добавить занятие' : 'Изменить занятие' }}
          </div>
        </div>
        <button class="btn" type="button" @click="closeForm">Закрыть</button>
      </div>

      <div class="form" style="margin-top: 12px;">
        <div>
          <div class="label">Предмет</div>
          <input v-model="form.subject" class="input" type="text" placeholder="Например, Алгебра" />
        </div>

        <div class="grid grid-cols-2">
          <div>
            <div class="label">Дата</div>
            <input v-model="form.startDate" class="input" type="date" />
          </div>
          <div>
            <div class="label">Время начала</div>
            <input v-model="form.startTime" class="input" type="time" step="1800" />
          </div>
        </div>

        <div>
          <div class="label">Продолжительность (мин)</div>
          <select v-model.number="form.durationMins" class="input">
            <option v-for="d in durationOptions" :key="d" :value="d">{{ d }}</option>
          </select>
        </div>

        <label class="row" style="justify-content: flex-start; gap: 8px;">
          <input v-model="form.isRecurringWeekly" type="checkbox" />
          <span>Повторять каждую неделю в это же время</span>
        </label>

        <div>
          <div class="label">Ученики</div>
          <div class="student-selector">
            <div
              v-for="s in activeStudents"
              :key="s.id"
              class="student-row"
              :class="{ 'student-row--selected': form.studentIds.includes(s.id) }"
            >
              <span
                class="student-name"
                :class="{ 'student-name--selected': form.studentIds.includes(s.id) }"
              >
                {{ s.name }}
              </span>
              <button
                type="button"
                class="btn btn-icon"
                @click="toggleStudent(s.id)"
              >
                {{ form.studentIds.includes(s.id) ? '–' : '+' }}
              </button>
            </div>
          </div>
          <div class="muted" style="margin-top: 6px;">Выбрано: {{ form.studentIds.length }}</div>
        </div>

        <div>
          <div class="label">Ссылка на встречу (необязательно)</div>
          <input v-model="form.meetingUrl" class="input" type="url" placeholder="https://..." />
        </div>

        <div v-if="apiError || schedule.error" style="color: #ef4444;">
          {{ apiError || schedule.error }}
        </div>

        <div class="row" style="margin-top: 6px;">
          <button class="btn" type="button" @click="closeForm">Отмена</button>
          <button
            class="btn btn-primary"
            type="button"
            @click="submitForm"
            :disabled="!form.subject.trim() || form.studentIds.length === 0"
          >
            Сохранить
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.schedule-card {
  border-radius: 16px;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.35);
  z-index: 30;
}

.modal {
  position: fixed;
  top: 84px;
  left: 50%;
  transform: translateX(-50%);
  width: min(920px, calc(100vw - 24px));
  max-height: calc(100vh - 120px);
  overflow: auto;
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 14px;
  z-index: 31;
}

.modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.details-grid {
  margin-top: 12px;
  display: grid;
  grid-template-columns: repeat(2, minmax(160px, 1fr));
  gap: 10px;
}

.detail-item {
  background: rgba(59, 130, 246, 0.06);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 10px;
  padding: 10px;
}

.chips-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 6px;
}

.confirm-box {
  margin-top: 12px;
  border: 1px solid rgba(239, 68, 68, 0.4);
  background: rgba(239, 68, 68, 0.08);
  border-radius: 10px;
  padding: 10px;
}

.btn-danger {
  border-color: rgba(239, 68, 68, 0.4);
  color: #b91c1c;
}

/* Стили для нового селектора учеников */
.student-selector {
  border: 1px solid var(--border);
  border-radius: 10px;
  max-height: 200px;
  overflow-y: auto;
  background: #fff;
}

.student-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 10px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
}

.student-row:last-child {
  border-bottom: none;
}

.student-row--selected {
  background: rgba(59, 130, 246, 0.06);
}

.student-name--selected {
  text-decoration: underline;
  text-underline-offset: 3px;
  font-weight: 600;
}

.btn-icon {
  width: 28px;
  height: 28px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: #fff;
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
  padding: 0;
}

.btn-icon:hover {
  background: var(--primary-light);
}
</style>
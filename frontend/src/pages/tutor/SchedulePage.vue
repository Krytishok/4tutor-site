<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import WeekCalendar from '../../components/calendar/WeekCalendar.vue'
import { useScheduleStore } from '../../stores/schedule'
import { useAuthStore } from '../../stores/auth'
import { useStudentsStore } from '../../stores/students'
import type { ScheduleEvent, StudentGroupType } from '../../types/domain'

const schedule = useScheduleStore()
const auth = useAuthStore()
const students = useStudentsStore()

onMounted(() => {
  if (students.getAll.length === 0) students.seedForRole('tutor')
  if (schedule.getEvents.length === 0) schedule.seedForRole(auth.role ?? 'tutor')
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
const form = ref<{
  groupType: StudentGroupType
  subject: string
  startDate: string // YYYY-MM-DD
  startTime: string // HH:mm
  durationMins: number
  studentId: string
  studentIds: string[]
}>({
  groupType: 'private',
  subject: '',
  startDate: new Date().toISOString().slice(0, 10),
  startTime: '18:00',
  durationMins: 60,
  studentId: '',
  studentIds: [],
})

const privateStudents = computed(() => students.getByGroup('private'))
const groupStudents = computed(() => students.getByGroup('group'))

const durationOptions = [30, 45, 60, 75, 90, 120]
const defaultDuration = durationOptions[0] ?? 60

function defaultPrivateStudentId() {
  return privateStudents.value[0]?.id ?? ''
}

function defaultGroupStudentIds() {
  return groupStudents.value.slice(0, 2).map((s) => s.id)
}

function openCreate() {
  formMode.value = 'create'
  form.value.groupType = 'private'
  form.value.subject = ''
  form.value.startDate = new Date().toISOString().slice(0, 10)
  form.value.startTime = '18:00'
  form.value.durationMins = 60
  form.value.studentId = privateStudents.value[0]?.id ?? ''
  form.value.studentIds = groupStudents.value.slice(0, 2).map((s) => s.id)
  isFormOpen.value = true
  isDetailsOpen.value = false
}

function openEdit(ev: ScheduleEvent) {
  formMode.value = 'edit'
  form.value.groupType = ev.groupType
  form.value.subject = ev.subject
  const start = new Date(ev.startAt)
  const end = new Date(ev.endAt)
  form.value.startDate = start.toISOString().slice(0, 10)
  form.value.startTime = `${String(start.getHours()).padStart(2, '0')}:${String(start.getMinutes()).padStart(2, '0')}`
  const rawDuration = Math.max(30, Math.round((end.getTime() - start.getTime()) / 60000))
  const closest = durationOptions.reduce(
    (best, cur) => (Math.abs(cur - rawDuration) < Math.abs(best - rawDuration) ? cur : best),
    defaultDuration,
  )
  form.value.durationMins = closest

  if (ev.groupType === 'private') {
    form.value.studentId = ev.studentIds[0] ?? ''
    form.value.studentIds = [ev.studentIds[0] ?? ''].filter(Boolean)
  } else {
    form.value.studentId = ev.studentIds[0] ?? ''
    form.value.studentIds = ev.studentIds
  }

  isFormOpen.value = true
  isDetailsOpen.value = false
  selectedEvent.value = ev
}

function closeForm() {
  isFormOpen.value = false
}

function closeDetails() {
  isDetailsOpen.value = false
  selectedEvent.value = null
}

function formatTime(iso: string) {
  return new Date(iso).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' })
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

function submitForm() {
  const subject = form.value.subject.trim()
  if (!subject) return
  if (form.value.groupType === 'private') {
    if (!form.value.studentId) return
  } else {
    if (form.value.studentIds.length === 0) return
  }

  const start = buildLocalDateTime(form.value.startDate, form.value.startTime)
  const end = new Date(start.getTime() + form.value.durationMins * 60000)

  const payload = {
    groupType: form.value.groupType,
    subject,
    startAt: start.toISOString(),
    endAt: end.toISOString(),
    studentIds:
      form.value.groupType === 'private' ? [form.value.studentId] : form.value.studentIds,
  } satisfies Omit<ScheduleEvent, 'id'>

  if (formMode.value === 'create') {
    schedule.createEvent(payload)
  } else if (formMode.value === 'edit' && selectedEvent.value) {
    schedule.updateEvent(selectedEvent.value.id, payload)
  }

  closeForm()
  closeDetails()
}

function onSelectEvent(ev: ScheduleEvent) {
  selectedEvent.value = ev
  isDetailsOpen.value = true
}

function removeSelected() {
  if (!selectedEvent.value) return
  schedule.deleteEvent(selectedEvent.value.id)
  closeDetails()
}

function onGroupTypeChange(groupType: StudentGroupType) {
  form.value.groupType = groupType
  if (groupType === 'private') {
    form.value.studentId = defaultPrivateStudentId()
    form.value.studentIds = form.value.studentId ? [form.value.studentId] : []
  } else {
    const ids = defaultGroupStudentIds()
    form.value.studentIds = ids
    form.value.studentId = ids[0] ?? ''
  }
}

function studentName(id: string) {
  return studentsById.value[id] ?? '—'
}
</script>

<template>
  <div class="page">
    <div>
      <h1 class="page-title">Расписание</h1>
      <p class="muted" style="margin: 8px 0 0 0;">
        Календарь занятий в стиле Google: время слева, дни недели сверху. Блоки — это встречи.
      </p>
    </div>

    <div class="card">
      <div class="row" style="margin-bottom: 12px;">
        <div>
          <div class="card-title" style="margin-bottom: 4px;">Неделя</div>
          <div class="muted">Время обрезается по самому раннему занятию на неделе.</div>
        </div>
        <button class="btn btn-primary" type="button" @click="openCreate">
          Добавить занятие
        </button>
      </div>

      <WeekCalendar
        :events="events"
        :students-by-id="studentsById"
        @select="onSelectEvent"
      />
    </div>

    <!-- Details modal -->
    <div v-if="isDetailsOpen && selectedEvent" class="modal-backdrop" @click="closeDetails" />
    <div v-if="isDetailsOpen && selectedEvent" class="modal" role="dialog" aria-modal="true">
      <div class="modal-header">
        <div>
          <div class="card-title" style="font-size: 18px;">
            {{ selectedEvent.subject }}
          </div>
          <div class="muted" style="margin-top: 4px;">
            {{
              `${formatDate(selectedEvent.startAt)} • ${formatTime(selectedEvent.startAt)}–${formatTime(selectedEvent.endAt)}`
            }}
          </div>
        </div>
        <button class="btn" type="button" @click="closeDetails">Закрыть</button>
      </div>

      <div class="form" style="margin-top: 12px;">
        <div class="card">
          <div class="card-title">Тип занятия</div>
          <div class="muted" style="margin-top: 6px;">
            <span v-if="selectedEvent.groupType === 'group'">
              Групповое • {{ selectedEvent.studentIds.length }} учеников
            </span>
            <span v-else>
              Индивидуальное • {{ studentName(selectedEvent.studentIds[0] ?? '') }}
            </span>
          </div>
        </div>

        <div class="card">
          <div class="card-title">Ученики</div>
          <div class="muted" style="margin-top: 6px;">
            <div v-if="selectedEvent.groupType === 'group'" style="display: flex; gap: 8px; flex-wrap: wrap;">
              <span
                v-for="sid in selectedEvent.studentIds"
                :key="sid"
                class="chip"
              >
                {{ studentName(sid) }}
              </span>
            </div>
            <div v-else>
              {{ studentName(selectedEvent.studentIds[0] ?? '') }}
            </div>
          </div>
        </div>

        <div class="row">
          <button class="btn" type="button" @click="openEdit(selectedEvent)">
            Изменить
          </button>
          <button class="btn" type="button" @click="removeSelected">
            Удалить
          </button>
        </div>
      </div>
    </div>

    <!-- Add/Edit modal -->
    <div v-if="isFormOpen" class="modal-backdrop" @click="closeForm" />
    <div v-if="isFormOpen" class="modal" role="dialog" aria-modal="true" aria-label="Добавить или изменить занятие">
      <div class="modal-header">
        <div>
          <div class="card-title" style="font-size: 18px;">
            {{ formMode === 'create' ? 'Добавить занятие' : 'Изменить занятие' }}
          </div>
          <div class="muted" style="margin-top: 4px;">MVP: локальные данные (API заготовлен, но не вызывается).</div>
        </div>
        <button class="btn" type="button" @click="closeForm">Закрыть</button>
      </div>

      <div class="form" style="margin-top: 12px;">
        <div>
          <div class="label">Тип занятия</div>
          <div class="grid grid-cols-2">
            <button
              type="button"
              class="btn"
              :style="form.groupType === 'private' ? { borderColor: 'rgba(30, 58, 138, 0.6)' } : undefined"
              @click="onGroupTypeChange('private')"
            >
              Индивидуальное
            </button>
            <button
              type="button"
              class="btn"
              :style="form.groupType === 'group' ? { borderColor: 'rgba(30, 58, 138, 0.6)' } : undefined"
              @click="onGroupTypeChange('group')"
            >
              Групповое
            </button>
          </div>
        </div>

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
            <option v-for="d in durationOptions" :key="d" :value="d">
              {{ d }}
            </option>
          </select>
        </div>

        <div v-if="form.groupType === 'private'">
          <div class="label">Ученик</div>
          <select v-model="form.studentId" class="input">
            <option v-for="s in privateStudents" :key="s.id" :value="s.id">
              {{ s.name }}
            </option>
          </select>
        </div>

        <div v-else>
          <div class="label">Ученики (для групповых занятий)</div>
          <select v-model="form.studentIds" class="input" multiple size="5">
            <option v-for="s in groupStudents" :key="s.id" :value="s.id">
              {{ s.name }}
            </option>
          </select>
          <div class="muted" style="margin-top: 6px;">
            Выбрано: {{ form.studentIds.length }}
          </div>
        </div>

        <div class="row" style="margin-top: 6px;">
          <button class="btn" type="button" @click="closeForm">
            Отмена
          </button>
          <button
            class="btn btn-primary"
            type="button"
            @click="submitForm"
            :disabled="!form.subject.trim() || (form.groupType === 'private' ? !form.studentId : form.studentIds.length === 0)"
          >
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
</style>


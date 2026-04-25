<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import type { ScheduleEvent } from '../../types/domain'

type Props = {
  events: ScheduleEvent[]
  studentsById: Record<string, string>
  readonly?: boolean
  weekdaysOnly?: boolean
}

const props = defineProps<Props>()

const slotMinutes = 30
const defaultStartMinutes = 8 * 60
const defaultEndMinutes = 20 * 60
const timeAxisBufferMinutes = 30
const slotHeight = 42

function startOfWeekMonday(date: Date) {
  const d = new Date(date)
  const day = d.getDay()
  const diff = (day === 0 ? -6 : 1) - day
  d.setDate(d.getDate() + diff)
  d.setHours(0, 0, 0, 0)
  return d
}

function addDays(date: Date, days: number) {
  const d = new Date(date)
  d.setDate(d.getDate() + days)
  return d
}

function formatDayName(d: Date) {
  return d.toLocaleDateString('ru-RU', { weekday: 'short' }).replace('.', '')
}

function formatDayNumber(d: Date) {
  return d.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' })
}

function minutesBetween(a: Date, b: Date) {
  return (b.getTime() - a.getTime()) / 60000
}

function dateKeyLocal(d: Date) {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

function eventStartKey(event: ScheduleEvent) {
  return dateKeyLocal(new Date(event.startAt))
}

function colorFromString(input: string) {
  let h = 0
  for (let i = 0; i < input.length; i++) h = (h * 31 + input.charCodeAt(i)) >>> 0
  const pick = h % 5
  if (pick === 0) return { bg: '#dbeafe', border: '#60a5fa', text: '#1e3a8a' }
  if (pick === 1) return { bg: '#dcfce7', border: '#34d399', text: '#065f46' }
  if (pick === 2) return { bg: '#fef3c7', border: '#f59e0b', text: '#78350f' }
  if (pick === 3) return { bg: '#fae8ff', border: '#c084fc', text: '#6b21a8' }
  return { bg: '#fee2e2', border: '#f87171', text: '#7f1d1d' }
}

const currentDate = ref(new Date())
const now = ref(new Date())
let nowTimer: number | null = null

onMounted(() => {
  nowTimer = window.setInterval(() => {
    now.value = new Date()
  }, 60000)
})

onBeforeUnmount(() => {
  if (nowTimer !== null) window.clearInterval(nowTimer)
})

const weekStart = computed(() => startOfWeekMonday(currentDate.value))
const days = computed(() => {
  const daysCount = props.weekdaysOnly ? 5 : 7
  return Array.from({ length: daysCount }).map((_, idx) => {
    const d = addDays(weekStart.value, idx)
    return { idx, date: d, key: dateKeyLocal(d), label: formatDayName(d), dateLabel: formatDayNumber(d) }
  })
})

const weekEnd = computed(() => addDays(weekStart.value, 7))

// Генерация повторяющихся событий для текущей недели
const recurringInstances = computed<ScheduleEvent[]>(() => {
  const instances: ScheduleEvent[] = []
  const weekStartDate = weekStart.value
  const weekEndDate = weekEnd.value

  for (const ev of props.events) {
    if (!ev.isRecurringWeekly) continue
    const originalStart = new Date(ev.startAt)
    if (originalStart >= weekStartDate) continue // уже попадает в неделю

    const originalEnd = new Date(ev.endAt)
    const duration = originalEnd.getTime() - originalStart.getTime()

    let cursor = new Date(originalStart)
    while (cursor < weekStartDate) {
      cursor.setDate(cursor.getDate() + 7)
    }
    while (cursor < weekEndDate) {
      const instanceStart = new Date(cursor)
      const instanceEnd = new Date(instanceStart.getTime() + duration)

      const alreadyExists = props.events.some(e => {
        const eStart = new Date(e.startAt).getTime()
        return eStart === instanceStart.getTime() && e.id === ev.id
      })

      if (!alreadyExists) {
        instances.push({
          ...ev,
          id: `${ev.id}_${instanceStart.toISOString()}`, // фиктивный ID для предотвращения редактирования
          startAt: instanceStart.toISOString(),
          endAt: instanceEnd.toISOString(),
        })
      }
      cursor.setDate(cursor.getDate() + 7)
    }
  }
  return instances
})

// Объединённый список событий для отображения
const displayEvents = computed(() => {
  return [...props.events, ...recurringInstances.value]
})

const visibleRange = computed(() => {
  const intersecting = displayEvents.value.filter((ev) => {
    const s = new Date(ev.startAt)
    const e = new Date(ev.endAt)
    return e > weekStart.value && s < weekEnd.value
  })

  if (!intersecting.length) return { startTotal: defaultStartMinutes, endTotal: defaultEndMinutes }

  let minStart = Number.POSITIVE_INFINITY
  let maxEnd = Number.NEGATIVE_INFINITY
  for (const ev of intersecting) {
    const s = new Date(ev.startAt)
    const e = new Date(ev.endAt)
    minStart = Math.min(minStart, s.getHours() * 60 + s.getMinutes())
    maxEnd = Math.max(maxEnd, e.getHours() * 60 + e.getMinutes())
  }

  const startTotal = Math.max(0, Math.floor((minStart - timeAxisBufferMinutes) / slotMinutes) * slotMinutes)
  const endTotal = Math.min(24 * 60, Math.ceil((maxEnd + timeAxisBufferMinutes) / slotMinutes) * slotMinutes)
  return { startTotal, endTotal: Math.max(endTotal, startTotal + slotMinutes) }
})

const slotCount = computed(() => (visibleRange.value.endTotal - visibleRange.value.startTotal) / slotMinutes)
const calendarHeight = computed(() => slotCount.value * slotHeight)

const timeSlots = computed(() => {
  const slots: Array<{ label: string; minutes: number }> = []
  for (let i = 0; i < slotCount.value; i++) {
    const totalMinutes = visibleRange.value.startTotal + i * slotMinutes
    const h = Math.floor(totalMinutes / 60)
    const m = totalMinutes % 60
    slots.push({ label: `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`, minutes: i * slotMinutes })
  }
  return slots
})

function shiftWeek(deltaDays: number) {
  currentDate.value = addDays(currentDate.value, deltaDays)
}

function goToCurrentWeek() {
  currentDate.value = new Date()
}

function isSameWeekAsToday() {
  const ws = weekStart.value
  const we = weekEnd.value
  return now.value >= ws && now.value < we
}

// Линия текущего времени на всю ширину колонок
const nowLineAllDays = computed(() => {
  if (!isSameWeekAsToday()) return null
  const mins = now.value.getHours() * 60 + now.value.getMinutes()
  if (mins < visibleRange.value.startTotal || mins > visibleRange.value.endTotal) return null
  const top = ((mins - visibleRange.value.startTotal) / slotMinutes) * slotHeight
  return `${top}px`
})

function isEventInDayRange(event: ScheduleEvent, day: Date) {
  const eventStart = new Date(event.startAt)
  const eventEnd = new Date(event.endAt)
  const rangeStart = new Date(day)
  rangeStart.setHours(Math.floor(visibleRange.value.startTotal / 60), visibleRange.value.startTotal % 60, 0, 0)
  const rangeEnd = new Date(day)
  rangeEnd.setHours(Math.floor(visibleRange.value.endTotal / 60), visibleRange.value.endTotal % 60, 0, 0)
  return eventEnd > rangeStart && eventStart < rangeEnd
}

function eventBoxStyle(event: ScheduleEvent, day: Date) {
  const eventStart = new Date(event.startAt)
  const eventEnd = new Date(event.endAt)
  const rangeStart = new Date(day)
  rangeStart.setHours(Math.floor(visibleRange.value.startTotal / 60), visibleRange.value.startTotal % 60, 0, 0)
  const rangeEnd = new Date(day)
  rangeEnd.setHours(Math.floor(visibleRange.value.endTotal / 60), visibleRange.value.endTotal % 60, 0, 0)

  const start = new Date(Math.max(eventStart.getTime(), rangeStart.getTime()))
  const end = new Date(Math.min(eventEnd.getTime(), rangeEnd.getTime()))
  const startMins = minutesBetween(rangeStart, start)
  const durationMins = Math.max(1, minutesBetween(start, end))
  const top = (startMins / slotMinutes) * slotHeight
  const height = Math.max((durationMins / slotMinutes) * slotHeight, 26)
  const c = colorFromString(event.subject)

  return {
    top: `${top}px`,
    height: `${height}px`,
    background: c.bg,
    border: `1px solid ${c.border}`,
    color: c.text,
  }
}

function eventIsCompact(event: ScheduleEvent) {
  const mins = minutesBetween(new Date(event.startAt), new Date(event.endAt))
  return mins < 45
}

const emit = defineEmits<{ (e: 'select', event: ScheduleEvent): void }>()
function onSelect(event: ScheduleEvent) {
  if (!props.readonly) emit('select', event)
}

const weekLabel = computed(() => {
  const start = weekStart.value
  const end = addDays(weekStart.value, props.weekdaysOnly ? 4 : 6)
  const f = (d: Date) => d.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' })
  return `${f(start)} — ${f(end)}`
})
</script>

<template>
  <div class="calendar">
    <div class="calendar-toolbar">
      <div class="row" style="gap: 8px;">
        <button class="btn" type="button" @click="shiftWeek(-7)">←</button>
        <button class="btn" type="button" @click="shiftWeek(7)">→</button>
        <button class="btn" type="button" @click="goToCurrentWeek">Текущая неделя</button>
      </div>
      <div class="muted" style="font-weight: 800;">Неделя: {{ weekLabel }}</div>
    </div>

    <div class="week-grid" :style="{ '--days-count': String(days.length) }">
      <div class="week-header">
        <div class="time-spacer" />
        <div
          v-for="d in days"
          :key="d.key"
          class="day-header"
          :class="{ 'day-header--today': d.key === dateKeyLocal(now) }"
        >
          <div class="day-name">{{ d.label }}</div>
          <div class="day-date">{{ d.dateLabel }}</div>
        </div>
      </div>

      <div class="week-body-scroll">
        <div class="week-body" :style="{ '--calendar-height': `${calendarHeight}px`, '--slot-h': `${slotHeight}px` }">
          <div class="time-axis">
            <div v-for="slot in timeSlots" :key="slot.minutes" class="time-label" :style="{ height: `${slotHeight}px` }">
              {{ slot.label }}
            </div>
          </div>

          <div class="day-columns" :style="{ position: 'relative' }">
            <!-- Единая линия текущего времени на всю ширину -->
            <div v-if="nowLineAllDays" class="now-line-all" :style="{ top: nowLineAllDays }" />

            <div
              v-for="day in days"
              :key="day.key"
              class="day-column"
              :class="{ 'day-column--today': day.key === dateKeyLocal(now) }"
            >
              <div
                v-for="ev in displayEvents.filter((e) => eventStartKey(e) === day.key && isEventInDayRange(e, day.date))"
                :key="ev.id"
                class="event"
                :class="{ 'event--compact': eventIsCompact(ev) }"
                :style="{ ...eventBoxStyle(ev, day.date), cursor: props.readonly ? 'default' : 'pointer' }"
                @click="onSelect(ev)"
              >
                <div class="event-title">{{ ev.subject }}</div>
                <div class="event-time">
                  {{ new Date(ev.startAt).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' }) }}–{{
                    new Date(ev.endAt).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
                  }}
                </div>
                <div v-if="!eventIsCompact(ev)" class="event-meta">
                  <span v-if="ev.groupType === 'group'">Группа: {{ ev.studentIds.length }}</span>
                  <span v-else>
                    Ученик: {{ ev.studentIds[0] ? (props.studentsById[ev.studentIds[0]] ?? '—') : '—' }}
                  </span>
                  <span v-if="ev.isRecurringWeekly">Еженедельно</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.calendar {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.calendar-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 4px 0;
}

.week-grid {
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: var(--panel);
}

.week-header {
  display: grid;
  grid-template-columns: 92px repeat(var(--days-count), minmax(160px, 1fr));
  border-bottom: 1px solid var(--border);
  background: #fff;
}

.time-spacer {
  height: 58px;
}

.day-header {
  padding: 10px 12px;
  border-left: 1px solid rgba(229, 231, 235, 0.7);
}

/* Текущий день в шапке – мягкий зелёный */
.day-header--today {
  background: #ecfdf5;
  border: 1px solid #6ee7b7;
  border-radius: 6px;
}

.day-name {
  font-weight: 900;
  color: var(--primary);
}

.day-date {
  margin-top: 3px;
  color: var(--muted);
  font-weight: 800;
}

.week-body-scroll {
  overflow: auto;
}

.week-body {
  display: grid;
  grid-template-columns: 92px repeat(var(--days-count), minmax(160px, 1fr));
}

.time-axis {
  border-right: 1px solid rgba(229, 231, 235, 0.7);
}

.time-label {
  padding: 8px 10px;
  font-size: 12px;
  color: var(--muted);
  border-bottom: 1px solid rgba(229, 231, 235, 0.7);
  background: #fff;
}

.day-columns {
  grid-column: 2 / -1;
  display: grid;
  grid-template-columns: repeat(var(--days-count), minmax(160px, 1fr));
}

.day-column {
  position: relative;
  height: var(--calendar-height);
  background-image: repeating-linear-gradient(
    to bottom,
    rgba(107, 114, 128, 0.14) 0px,
    rgba(107, 114, 128, 0.14) 1px,
    transparent 1px,
    transparent
  );
  background-size: 100% var(--slot-h);
}

/* Текущий день в колонке */
.day-column--today {
  background-color: rgba(167, 243, 208, 0.15);
  box-shadow: inset 0 0 0 2px rgba(52, 211, 153, 0.4);
  border-radius: 4px;
}

/* Линия текущего времени через все дни */
.now-line-all {
  position: absolute;
  left: 0;
  right: 0;
  height: 2px;
  background: #ef4444;
  z-index: 5;
  pointer-events: none;
}

.event {
  position: absolute;
  left: 5px;
  right: 5px;
  border-radius: 10px;
  padding: 6px 8px;
  overflow: hidden;
  box-shadow: 0 1px 0 rgba(0, 0, 0, 0.05);
  z-index: 3;
}

.event-title {
  font-weight: 800;
  font-size: 12px;
  line-height: 1.2;
}

.event-time {
  font-size: 11px;
  margin-top: 3px;
  opacity: 0.9;
}

.event-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  font-size: 11px;
  margin-top: 4px;
  opacity: 0.9;
}

.event--compact .event-meta {
  display: none;
}
</style>
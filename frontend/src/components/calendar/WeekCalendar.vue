<script setup lang="ts">
import { computed, ref } from 'vue'
import type { ScheduleEvent } from '../../types/domain'

type Props = {
  events: ScheduleEvent[]
  studentsById: Record<string, string>
  readonly?: boolean
}

const props = defineProps<Props>()

const slotMinutes = 30
const defaultStartMinutes = 8 * 60
const defaultEndMinutes = 20 * 60
const timeAxisBufferMinutes = 0
const slotHeight = 42 // px

function startOfWeekMonday(date: Date) {
  const d = new Date(date)
  const day = d.getDay() // 0=Sun ... 6=Sat
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
  const x = new Date(d)
  return `${x.getFullYear()}-${String(x.getMonth() + 1).padStart(2, '0')}-${String(x.getDate()).padStart(2, '0')}`
}

function eventStartKey(event: ScheduleEvent) {
  return dateKeyLocal(new Date(event.startAt))
}

function colorFromString(input: string) {
  // Simple hash to pick a palette color deterministically.
  let h = 0
  for (let i = 0; i < input.length; i++) h = (h * 31 + input.charCodeAt(i)) >>> 0
  const pick = h % 4
  if (pick === 0) return { bg: 'rgba(30, 58, 138, 0.16)', border: 'rgba(30, 58, 138, 0.45)', text: '#1E3A8A' }
  if (pick === 1) return { bg: 'rgba(16, 185, 129, 0.16)', border: 'rgba(16, 185, 129, 0.45)', text: '#10B981' }
  if (pick === 2) return { bg: 'rgba(245, 158, 11, 0.16)', border: 'rgba(245, 158, 11, 0.45)', text: '#F59E0B' }
  return { bg: 'rgba(239, 68, 68, 0.16)', border: 'rgba(239, 68, 68, 0.45)', text: '#EF4444' }
}

const currentDate = ref(new Date())
const weekStart = computed(() => startOfWeekMonday(currentDate.value))

const days = computed(() => {
  return Array.from({ length: 7 }).map((_, idx) => {
    const d = addDays(weekStart.value, idx)
    return {
      idx,
      date: d,
      key: dateKeyLocal(d),
      label: formatDayName(d),
      dateLabel: formatDayNumber(d),
    }
  })
})

const weekEnd = computed(() => addDays(weekStart.value, 7))

const visibleRange = computed(() => {
  const intersecting = props.events.filter((ev) => {
    const s = new Date(ev.startAt)
    const e = new Date(ev.endAt)
    return e > weekStart.value && s < weekEnd.value
  })

  if (intersecting.length === 0) {
    return { startTotal: defaultStartMinutes, endTotal: defaultEndMinutes }
  }

  let minStart = Number.POSITIVE_INFINITY
  let maxEnd = Number.NEGATIVE_INFINITY

  for (const ev of intersecting) {
    const s = new Date(ev.startAt)
    const e = new Date(ev.endAt)
    const sTotal = s.getHours() * 60 + s.getMinutes()
    const eTotal = e.getHours() * 60 + e.getMinutes()
    minStart = Math.min(minStart, sTotal)
    maxEnd = Math.max(maxEnd, eTotal)
  }

  const startTotal =
    Math.max(
      0,
      Math.floor((minStart - timeAxisBufferMinutes) / slotMinutes) * slotMinutes,
    )

  const endTotal = Math.min(
    24 * 60,
    Math.ceil(maxEnd / slotMinutes) * slotMinutes,
  )

  const safeEndTotal = Math.max(endTotal, startTotal + slotMinutes)
  return { startTotal, endTotal: safeEndTotal }
})

const slotCount = computed(() => (visibleRange.value.endTotal - visibleRange.value.startTotal) / slotMinutes)
const calendarHeight = computed(() => slotCount.value * slotHeight)

const timeSlots = computed(() => {
  const slots: Array<{ label: string; minutes: number }> = []
  for (let i = 0; i < slotCount.value; i++) {
    const totalMinutes = visibleRange.value.startTotal + i * slotMinutes
    const h = Math.floor(totalMinutes / 60)
    const m = totalMinutes % 60
    const label = `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`
    slots.push({ label, minutes: i * slotMinutes })
  }
  return slots
})

function shiftWeek(deltaDays: number) {
  const next = addDays(currentDate.value, deltaDays)
  currentDate.value = next
}

function isEventInDayRange(event: ScheduleEvent, day: Date) {
  const eventStart = new Date(event.startAt)
  const eventEnd = new Date(event.endAt)

  const rangeStart = new Date(day)
  rangeStart.setHours(
    Math.floor(visibleRange.value.startTotal / 60),
    visibleRange.value.startTotal % 60,
    0,
    0,
  )
  const rangeEnd = new Date(day)
  rangeEnd.setHours(
    Math.floor(visibleRange.value.endTotal / 60),
    visibleRange.value.endTotal % 60,
    0,
    0,
  )

  return eventEnd > rangeStart && eventStart < rangeEnd
}

function eventBoxStyle(event: ScheduleEvent, day: Date) {
  const eventStart = new Date(event.startAt)
  const eventEnd = new Date(event.endAt)

  const rangeStart = new Date(day)
  rangeStart.setHours(
    Math.floor(visibleRange.value.startTotal / 60),
    visibleRange.value.startTotal % 60,
    0,
    0,
  )
  const rangeEnd = new Date(day)
  rangeEnd.setHours(
    Math.floor(visibleRange.value.endTotal / 60),
    visibleRange.value.endTotal % 60,
    0,
    0,
  )

  const start = new Date(Math.max(eventStart.getTime(), rangeStart.getTime()))
  const end = new Date(Math.min(eventEnd.getTime(), rangeEnd.getTime()))

  const startMins = minutesBetween(rangeStart, start)
  const durationMins = Math.max(1, minutesBetween(start, end))

  const top = (startMins / slotMinutes) * slotHeight
  const height = (durationMins / slotMinutes) * slotHeight

  const c = colorFromString(event.subject)

  return {
    top: `${top}px`,
    height: `${height}px`,
    background: c.bg,
    border: `1px solid ${c.border}`,
    color: c.text,
  }
}

const emit = defineEmits<{
  (e: 'select', event: ScheduleEvent): void
}>()

function onSelect(event: ScheduleEvent) {
  if (props.readonly) return
  emit('select', event)
}

const weekLabel = computed(() => {
  const start = weekStart.value
  const end = addDays(weekStart.value, 6)
  const f = (d: Date) =>
    d.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' })
  return `${f(start)} — ${f(end)}`
})
</script>

<template>
  <div class="calendar">
    <div class="calendar-toolbar">
      <div class="row" style="gap: 12px;">
        <button class="btn" type="button" @click="shiftWeek(-7)">←</button>
        <button class="btn" type="button" @click="currentDate = new Date()">Сегодня</button>
        <button class="btn" type="button" @click="shiftWeek(7)">→</button>
      </div>
      <div class="muted" style="font-weight: 800;">Неделя: {{ weekLabel }}</div>
    </div>

    <div class="week-grid">
      <div class="week-header">
        <div class="time-spacer" />
        <div v-for="d in days" :key="d.key" class="day-header">
          <div class="day-name">{{ d.label }}</div>
          <div class="day-date">{{ d.dateLabel }}</div>
        </div>
      </div>

      <div class="week-body-scroll">
        <div
          class="week-body"
          :style="{ '--calendar-height': `${calendarHeight}px`, '--slot-h': `${slotHeight}px` }"
        >
          <div class="time-axis">
            <div
              v-for="slot in timeSlots"
              :key="slot.minutes"
              class="time-label"
              :style="{ height: `${slotHeight}px` }"
            >
              {{ slot.label }}
            </div>
          </div>

          <div class="day-columns">
            <div v-for="day in days" :key="day.key" class="day-column">
              <div
                v-for="ev in props.events.filter((e) => eventStartKey(e) === day.key && isEventInDayRange(e, day.date))"
                :key="ev.id"
                class="event"
                :style="{ ...eventBoxStyle(ev, day.date), cursor: props.readonly ? 'default' : 'pointer' }"
                @click="onSelect(ev)"
              >
                <div style="font-weight: 900; font-size: 13px; line-height: 1.2;">
                  {{ ev.subject }}
                </div>
                <div class="muted" style="font-size: 12px; margin-top: 4px;">
                  <span v-if="ev.groupType === 'group'">
                    Групповое • {{ ev.studentIds.length }} учеников
                  </span>
                  <span v-else>
                    Индивидуальное • {{ ev.studentIds[0] ? (props.studentsById[ev.studentIds[0]] ?? '—') : '—' }}
                  </span>
                </div>
                <div class="muted" style="font-size: 12px; margin-top: 6px;">
                  {{
                    new Date(ev.startAt).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
                  }}
                  –
                  {{
                    new Date(ev.endAt).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
                  }}
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
  grid-template-columns: 92px repeat(7, minmax(160px, 1fr));
  border-bottom: 1px solid var(--border);
  background: var(--panel);
}

.time-spacer {
  height: 64px;
}

.day-header {
  padding: 12px 12px;
  border-left: 1px solid rgba(229, 231, 235, 0.7);
}

.day-header:first-child {
  border-left: none;
}

.day-name {
  font-weight: 900;
  color: var(--primary);
  letter-spacing: -0.01em;
}

.day-date {
  margin-top: 4px;
  color: var(--muted);
  font-weight: 800;
}

.week-body-scroll {
  overflow: auto;
}

.week-body {
  display: grid;
  grid-template-columns: 92px repeat(7, minmax(160px, 1fr));
  /* height is set by inline style via --calendar-height */
}

.time-axis {
  border-right: 1px solid rgba(229, 231, 235, 0.7);
  padding: 0;
}

.time-label {
  padding: 8px 10px;
  font-size: 12px;
  color: var(--muted);
  border-bottom: 1px solid rgba(229, 231, 235, 0.7);
  background: var(--panel);
  position: sticky;
  left: 0;
  z-index: 1;
}

.day-columns {
  grid-column: 2 / -1;
  display: grid;
  grid-template-columns: repeat(7, minmax(160px, 1fr));
}

.day-column {
  position: relative;
  height: var(--calendar-height);
  background-image: repeating-linear-gradient(
    to bottom,
    rgba(107, 114, 128, 0.18) 0px,
    rgba(107, 114, 128, 0.18) 1px,
    transparent 1px,
    transparent
  );
  background-size: 100% var(--slot-h);
}

.event {
  position: absolute;
  left: 6px;
  right: 6px;
  border-radius: 12px;
  padding: 10px 10px;
  overflow: hidden;
  box-shadow: 0 1px 0 rgba(0, 0, 0, 0.02);
}
</style>


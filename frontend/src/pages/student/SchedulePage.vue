<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useScheduleStore } from '../../stores/schedule'
import { useAuthStore } from '../../stores/auth'
import WeekCalendar from '../../components/calendar/WeekCalendar.vue'
import { useStudentsStore } from '../../stores/students'

const schedule = useScheduleStore()
const auth = useAuthStore()
const students = useStudentsStore()

onMounted(() => {
  if (students.getAll.length === 0) students.seedForRole(auth.role ?? 'student')
  if (schedule.getEvents.length === 0) schedule.seedForRole(auth.role ?? 'student')
})

const events = computed(() => schedule.getEvents)

const studentsById = computed<Record<string, string>>(() => {
  const map: Record<string, string> = {}
  for (const s of students.getAll) map[s.id] = s.name
  return map
})
</script>

<template>
  <div class="page">
    <div>
      <h1 class="page-title">Моё расписание</h1>
      <p class="muted" style="margin: 8px 0 0 0;">
        Ближайшие занятия на неделю.
      </p>
    </div>

    <div class="card">
      <WeekCalendar :events="events" :students-by-id="studentsById" :readonly="true" />
    </div>
  </div>
</template>


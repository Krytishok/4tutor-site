<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useScheduleStore } from '../../stores/schedule'
import WeekCalendar from '../../components/calendar/WeekCalendar.vue'

const schedule = useScheduleStore()

onMounted(() => {
  void schedule.loadEvents()
})

const events = computed(() => schedule.getEvents)
</script>

<template>
  <div class="page">
    <div>
      <h1 class="page-title">Моё расписание</h1>
      <p class="muted" style="margin: 8px 0 0 0;">Все уроки, назначенные репетиторами.</p>
    </div>

    <div class="card">
      <WeekCalendar :events="events" :students-by-id="{}" :readonly="true" />
    </div>
  </div>
</template>

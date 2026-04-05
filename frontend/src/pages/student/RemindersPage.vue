<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { useNotificationsStore } from '../../stores/notifications'
import type { Role } from '../../types/roles'

const auth = useAuthStore()
const notifications = useNotificationsStore()

const role = computed<Role>(() => (auth.role ?? 'student') as Role)

onMounted(() => {
  notifications.seedForRole(role.value)
})

const openReminders = computed(() => notifications.getOpenByRole(role.value))

function done(id: string) {
  notifications.markDone(id)
}

function formatDueAt(iso: string) {
  try {
    return new Date(iso).toLocaleString()
  } catch {
    return iso
  }
}

function dueBadge(iso: string) {
  const due = new Date(iso).getTime()
  const now = Date.now()
  if (Number.isNaN(due)) return { label: '', cls: '' }
  if (due < now) return { label: 'Просрочено', cls: 'chip-danger' }
  const hours = (due - now) / (1000 * 60 * 60)
  if (hours <= 24) return { label: 'Скоро', cls: 'chip-warning' }
  return { label: 'В срок', cls: '' }
}
</script>

<template>
  <div class="page">
    <div>
      <h1 class="page-title">Напоминания</h1>
      <p class="muted" style="margin: 8px 0 0 0;">
        Дедлайны заданий и ближайшие события.
      </p>
    </div>

    <div class="card">
      <div class="row">
        <div>
          <div class="card-title">Открытые</div>
          <div class="muted">Отметьте, когда задание выполнено</div>
        </div>
        <span class="chip">{{ openReminders.length }} шт.</span>
      </div>

      <div style="margin-top: 12px; display: flex; flex-direction: column; gap: 10px;">
        <div v-if="openReminders.length === 0" class="muted">Нет напоминаний.</div>

        <div v-for="r in openReminders" :key="r.id" class="card" style="padding: 12px;">
          <div class="row" style="align-items: flex-start;">
            <div style="flex: 1;">
              <div style="font-weight: 800; margin-bottom: 4px;">
                {{ r.title }}
                <span v-if="dueBadge(r.dueAt).label" class="chip" :class="dueBadge(r.dueAt).cls" style="margin-left: 10px;">
                  {{ dueBadge(r.dueAt).label }}
                </span>
              </div>
              <div class="muted" style="font-size: 13px;">
                Срок: {{ formatDueAt(r.dueAt) }}
              </div>
            </div>
            <button class="btn btn-primary" type="button" @click="done(r.id)">
              Готово
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>


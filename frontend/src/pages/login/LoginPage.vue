<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { useNotificationsStore } from '../../stores/notifications'
import { useStudentsStore } from '../../stores/students'
import { useScheduleStore } from '../../stores/schedule'
import type { Role } from '../../types/roles'
import { ROLE_LABEL, ROLE_NAV } from '../../types/roles'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const notifications = useNotificationsStore()
const students = useStudentsStore()
const schedule = useScheduleStore()

const appName = import.meta.env.VITE_APP_NAME ?? '4tutor'

const selectedRole = ref<Role>('tutor')
const name = ref('')
const email = ref('')

const redirectTo = computed(() => {
  const value = route.query.redirect
  if (typeof value === 'string') return value
  return null
})

function submit() {
  const cleanName = name.value.trim()
  const cleanEmail = email.value.trim()
  if (!cleanName || !cleanEmail) return

  auth.loginAs({
    role: selectedRole.value,
    name: cleanName,
    email: cleanEmail,
  })

  notifications.seedForRole(selectedRole.value)
  students.seedForRole(selectedRole.value)
  schedule.seedForRole(selectedRole.value)

  const target =
    redirectTo.value ?? ROLE_NAV[selectedRole.value]?.[0]?.to ?? `/app/${selectedRole.value}`
  router.push(target)
}
</script>

<template>
  <div class="container">
    <div class="page">
      <div class="card">
        <div class="row">
          <div>
            <div class="page-title" style="margin-bottom: 4px;">{{ appName }}</div>
            <div class="muted" style="font-weight: 700;">
              Сервис для репетиторов и учеников
            </div>
          </div>
        </div>
      </div>

      <div class="card">
        <h2 class="card-title">Вход (MVP-заглушка)</h2>
        <p class="muted" style="margin: 0 0 14px 0;">
          Выберите роль и войдите — это временно, пока нет реального API.
        </p>

        <div class="grid grid-cols-2" style="margin-bottom: 14px;">
          <button
            type="button"
            class="btn"
            :style="selectedRole === 'student' ? { borderColor: 'rgba(30, 58, 138, 0.6)' } : undefined"
            @click="selectedRole = 'student'"
          >
            {{ ROLE_LABEL.student }}
          </button>
          <button
            type="button"
            class="btn"
            :style="selectedRole === 'tutor' ? { borderColor: 'rgba(30, 58, 138, 0.6)' } : undefined"
            @click="selectedRole = 'tutor'"
          >
            {{ ROLE_LABEL.tutor }}
          </button>
        </div>

        <form class="form" @submit.prevent="submit">
          <div>
            <div class="label">Имя</div>
            <input v-model="name" class="input" type="text" placeholder="Например, Анна" />
          </div>

          <div>
            <div class="label">Email</div>
            <input v-model="email" class="input" type="email" placeholder="name@example.com" />
          </div>

          <button class="btn btn-primary" type="submit" :disabled="!name.trim() || !email.trim()">
            Продолжить
          </button>
        </form>
      </div>
    </div>
  </div>
</template>


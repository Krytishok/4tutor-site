import { defineStore } from 'pinia'
import type { Role } from '../types/roles'

export type ReminderKind = 'assignment' | 'session'

export type Reminder = {
  id: string
  role: Role
  kind: ReminderKind
  title: string
  dueAt: string // ISO string
  status: 'open' | 'done'
}

const sampleReminders: Reminder[] = [
  {
    id: 'r1',
    role: 'student',
    kind: 'assignment',
    title: 'Задание: тест по алгебре (срок сегодня)',
    dueAt: new Date(Date.now() + 60 * 60 * 1000).toISOString(),
    status: 'open',
  },
  {
    id: 'r2',
    role: 'tutor',
    kind: 'assignment',
    title: 'Просроченное задание: домашка по русскому (не сдано)',
    dueAt: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
    status: 'open',
  },
]

export const useNotificationsStore = defineStore('notifications', {
  state: () => ({
    reminders: [] as Reminder[],
  }),
  getters: {
    getOpenByRole: (state) => (role: Role) =>
      state.reminders.filter((r) => r.role === role && r.status === 'open'),
    getDoneByRole: (state) => (role: Role) =>
      state.reminders.filter((r) => r.role === role && r.status === 'done'),
  },
  actions: {
    seedForRole(role: Role) {
      // For the MVP we seed demo data; later this will be replaced with API calls.
      this.reminders = sampleReminders.filter((r) => r.role === role)
    },
    markDone(id: string) {
      const item = this.reminders.find((r) => r.id === id)
      if (item) item.status = 'done'
    },
  },
})


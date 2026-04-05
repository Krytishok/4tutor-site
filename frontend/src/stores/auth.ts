import { defineStore } from 'pinia'
import type { Role } from '../types/roles'

export type AuthUser = {
  id: string
  name: string
  email: string
  role: Role
}

const STORAGE_KEY = '4tutor_auth_v1'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as AuthUser | null,
  }),
  getters: {
    isAuthed: (state) => Boolean(state.user),
    role: (state) => state.user?.role ?? null,
    name: (state) => state.user?.name ?? '',
    email: (state) => state.user?.email ?? '',
  },
  actions: {
    hydrate() {
      try {
        if (typeof window === 'undefined') return
        const raw = window.localStorage.getItem(STORAGE_KEY)
        if (!raw) return
        const parsed = JSON.parse(raw) as AuthUser
        if (parsed?.role && parsed?.email && parsed?.name) {
          this.user = parsed
        }
      } catch {
        // If storage is corrupted, just ignore it.
      }
    },
    loginAs(payload: { role: Role; name: string; email: string }) {
      this.user = {
        id: 'local-user',
        role: payload.role,
        name: payload.name,
        email: payload.email,
      }
      try {
        window.localStorage.setItem(STORAGE_KEY, JSON.stringify(this.user))
      } catch {
        // Storage might be disabled; keep in-memory session.
      }
    },
    logout() {
      this.user = null
      try {
        window.localStorage.removeItem(STORAGE_KEY)
      } catch {
        // ignore
      }
    },
  },
})


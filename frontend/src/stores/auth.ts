import { defineStore } from 'pinia'
import type { Role } from '../types/roles'
import {
  attachTokensToClient,
  fetchCurrentUser,
  obtainTokenPair,
  type UserProfile,
} from '../api/auth'
import { toApiError } from '../api/http'
import { refreshAccessToken } from '../api/tokenRefresh'
import {
  clearAuthTokens,
  getAccessToken,
  getRefreshToken,
  setAuthTokens,
} from '../api/authTokens'

export type AuthUser = {
  id: string
  name: string
  email: string
  role: Role
}

const STORAGE_KEY = '4tutor_auth_v1'

type PersistedAuth = {
  user: AuthUser
  access: string
  refresh: string
}

function profileToUser(profile: UserProfile): AuthUser {
  const name = `${profile.first_name} ${profile.last_name}`.trim() || profile.email
  return {
    id: String(profile.id),
    email: profile.email,
    name,
    role: profile.role,
  }
}

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
        const parsed = JSON.parse(raw) as Partial<PersistedAuth>
        if (typeof parsed.refresh !== 'string' || typeof parsed.access !== 'string') return
        if (!parsed.user?.role || !parsed.user?.email || !parsed.user?.id) return
        setAuthTokens(parsed.access, parsed.refresh)
        this.user = parsed.user
      } catch {
        // If storage is corrupted, ignore.
      }
    },

    persist() {
      if (!this.user) return
      const access = getAccessToken()
      const refresh = getRefreshToken()
      if (!refresh || !access) return
      const payload: PersistedAuth = {
        user: this.user,
        access,
        refresh,
      }
      try {
        window.localStorage.setItem(STORAGE_KEY, JSON.stringify(payload))
      } catch {
        // Storage might be disabled.
      }
    },

    patchStoredAccess(access: string) {
      try {
        if (typeof window === 'undefined') return
        const raw = window.localStorage.getItem(STORAGE_KEY)
        if (!raw) return
        const parsed = JSON.parse(raw) as Partial<PersistedAuth>
        if (typeof parsed.refresh !== 'string') return
        parsed.access = access
        if (parsed.user) {
          window.localStorage.setItem(STORAGE_KEY, JSON.stringify(parsed as PersistedAuth))
        }
      } catch {
        // ignore
      }
    },

    async validateSession() {
      if (!getRefreshToken()) return
      try {
        const profile = await fetchCurrentUser()
        this.user = profileToUser(profile)
        this.persist()
      } catch (err) {
        const { status } = toApiError(err)
        if (status !== 401 && status !== 403) {
          return
        }
        try {
          await refreshAccessToken()
          const profile = await fetchCurrentUser()
          this.user = profileToUser(profile)
          this.persist()
        } catch {
          this.logout()
        }
      }
    },

    async loginWithPassword(email: string, password: string) {
      const tokens = await obtainTokenPair(email.trim(), password)
      attachTokensToClient(tokens)
      const profile = await fetchCurrentUser()
      this.user = profileToUser(profile)
      this.persist()
    },

    logout() {
      this.user = null
      clearAuthTokens()
      try {
        window.localStorage.removeItem(STORAGE_KEY)
      } catch {
        // ignore
      }
    },
  },
})

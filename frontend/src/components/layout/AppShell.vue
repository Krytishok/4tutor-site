<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter, RouterLink, RouterView } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { ROLE_LABEL, ROLE_NAV, type NavItem, type Role } from '../../types/roles'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const appName = import.meta.env.VITE_APP_NAME ?? '4tutor'

const role = computed<Role | null>(() => {
  const metaRole = route.meta.role as Role | undefined
  return metaRole ?? auth.role
})

const navItems = computed<NavItem[]>(() => {
  if (!role.value) return []
  return ROLE_NAV[role.value]
})

const isDrawerOpen = ref(false)

function closeDrawer() {
  isDrawerOpen.value = false
}

function logout() {
  closeDrawer()
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <div class="app-shell">
    <header class="topbar">
      <div class="topbar-inner">
        <div class="brand">
          <div class="brand-title">{{ appName }}</div>
          <div class="brand-subtitle">CRM, задания и напоминания</div>
        </div>

        <div style="display: flex; align-items: center; gap: 12px;">
          <span v-if="role" class="chip" aria-label="Текущая роль">
            {{ ROLE_LABEL[role] }}
          </span>

          <span v-if="auth.isAuthed" class="muted" style="font-weight: 700;">
            {{ auth.name }}
          </span>

          <button
            v-if="!auth.isAuthed"
            class="btn"
            type="button"
            @click="router.push('/login')"
          >
            Вход
          </button>

          <button
            v-else
            class="btn mobile-only"
            type="button"
            @click="isDrawerOpen = true"
          >
            Меню
          </button>

          <button v-if="auth.isAuthed" class="btn" type="button" @click="logout">
            Выйти
          </button>
        </div>
      </div>
    </header>

    <div class="container">
      <div class="app-layout">
        <aside class="sidebar desktop-only">
          <nav class="nav" aria-label="Навигация">
            <RouterLink
              v-for="item in navItems"
              :key="item.to"
              :to="item.to"
              class="nav-item"
              @click="closeDrawer"
            >
              {{ item.label }}
            </RouterLink>
          </nav>
        </aside>

        <main>
          <RouterView />
        </main>
      </div>
    </div>

    <div v-if="isDrawerOpen" class="drawer-backdrop" @click="closeDrawer" />
    <div v-if="isDrawerOpen" class="drawer" role="dialog" aria-modal="true">
      <div class="drawer-actions">
        <div class="muted" style="font-weight: 800;">Навигация</div>
        <button class="btn" type="button" @click="closeDrawer">
          Закрыть
        </button>
      </div>
      <nav class="nav" aria-label="Навигация">
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="nav-item"
          @click="closeDrawer"
        >
          {{ item.label }}
        </RouterLink>
      </nav>
    </div>
  </div>
</template>

<style scoped>
</style>


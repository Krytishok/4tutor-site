import { createApp } from 'vue'
import { createPinia, setActivePinia } from 'pinia'
import App from './App.vue'
import { useAuthStore } from './stores/auth'
import router from './router'
import { setAuthFailureHandler } from './api/http'
import { setOnAccessRefreshed } from './api/authTokens'
import './style.css'

const pinia = createPinia()
setActivePinia(pinia)

const app = createApp(App)
app.use(pinia)
app.use(router)

const auth = useAuthStore()
setOnAccessRefreshed((access) => auth.patchStoredAccess(access))
setAuthFailureHandler(() => {
  auth.logout()
  router.replace({ path: '/login' })
})

auth.hydrate()

void auth.validateSession().finally(() => {
  app.mount('#app')
})

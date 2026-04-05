import { createApp } from 'vue'
import { createPinia, setActivePinia } from 'pinia'
import App from './App.vue'
import { useAuthStore } from './stores/auth'
import router from './router'
import './style.css'

const pinia = createPinia()
setActivePinia(pinia)

const app = createApp(App)
app.use(pinia)
app.use(router)

useAuthStore().hydrate()

app.mount('#app')

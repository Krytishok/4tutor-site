<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { useNotificationsStore } from '../../stores/notifications'
import { useStudentsStore } from '../../stores/students'
import { useScheduleStore } from '../../stores/schedule'
import { ROLE_NAV } from '../../types/roles'
import { toApiError } from '../../api/http'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const notifications = useNotificationsStore()
const students = useStudentsStore()
const schedule = useScheduleStore()

const appName = import.meta.env.VITE_APP_NAME ?? '4tutor'

const email = ref('')
const password = ref('')
const showPassword = ref(false)
const submitting = ref(false)
const formError = ref('')

// Валидация
const errors = ref<{
  email?: string
  password?: string
}>({})

// Правила валидации
const validationRules = {
  email: { min: 5, max: 100, required: true, pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/ },
  password: { min: 6, max: 50, required: true, pattern: /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{6,}$/ },
}

function validateField(field: 'email' | 'password', value: string): string | undefined {
  const rules = validationRules[field]
  const trimmed = value.trim()

  if (rules.required && !trimmed) {
    return 'Обязательное поле'
  }
  
  if (trimmed) {
    if (trimmed.length < rules.min) {
      return `Минимум ${rules.min} ${rules.min === 2 ? 'символа' : 'символов'}`
    }
    if (trimmed.length > rules.max) {
      return `Максимум ${rules.max} символов`
    }
    if (rules.pattern && !rules.pattern.test(trimmed)) {
      if (field === 'email') return 'Некорректный email'
      if (field === 'password') return 'Минимум 6 символов, буквы и цифры'
      return 'Некорректный формат'
    }
  }
  
  return undefined
}

function handleBlur(field: 'email' | 'password', value: string) {
  // Автоматически убираем пробелы по краям при потере фокуса
  if (field === 'email') email.value = value.trim()
  if (field === 'password') password.value = value.trim()
  
  errors.value[field] = validateField(field, value)
}

function validateAll(): boolean {
  const newErrors: typeof errors.value = {}
  
  newErrors.email = validateField('email', email.value)
  newErrors.password = validateField('password', password.value)
  
  errors.value = newErrors
  return !Object.values(newErrors).some(Boolean)
}

const redirectTo = () => {
  const value = route.query.redirect
  if (typeof value === 'string') return value
  return null
}

function togglePasswordVisibility() {
  showPassword.value = !showPassword.value
}

async function submit() {
  if (!validateAll()) return
  formError.value = ''
  submitting.value = true
  const cleanEmail = email.value.trim()
  const cleanPassword = password.value

  try {
    await auth.loginWithPassword(cleanEmail, cleanPassword)
    const role = auth.role
    if (!role) {
      formError.value = 'Не удалось определить роль пользователя'
      return
    }
    notifications.seedForRole(role)
    students.seedForRole(role)
    schedule.seedForRole(role)

    const target =
      redirectTo() ?? ROLE_NAV[role]?.[0]?.to ?? `/app/${role}`
    await router.push(target)
  } catch (err) {
    formError.value = toApiError(err).message
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="login-wrapper">
    <div class="gradient-bg gradient-left"></div>
    <div class="content-wrapper">
      <div class="page">
        <div class="card form-card">
          <div class="row">
            <div>
              <div class="page-title" style="margin-bottom: 4px;">{{ appName }}</div>
              <div class="muted" style="font-weight: 700;">
                Сервис для репетиторов и учеников
              </div>
            </div>
          </div>
        </div>

        <div class="card form-card">
          <h2 class="card-title">Вход</h2>
          <p class="muted" style="margin: 0 0 20px 0;">
            Войдите в аккаунт с email и паролем, указанными при регистрации.
          </p>

          <div v-if="formError" class="form-error" role="alert">{{ formError }}</div>

          <form class="form" @submit.prevent="submit">
            <!-- Email -->
            <div class="form-group">
              <div class="label">Email</div>
              <div class="input-wrapper">
                <input 
                  v-model="email" 
                  class="input" 
                  :class="{ 'input--error': errors.email }"
                  type="email" 
                  placeholder="name@example.com"
                  maxlength="100"
                  @blur="handleBlur('email', email)"
                />
                <transition name="fade">
                  <div v-if="errors.email" class="error-tooltip error-tooltip--right">{{ errors.email }}</div>
                </transition>
              </div>
            </div>

            <!-- Пароль -->
            <div class="form-group">
              <div class="label">Пароль</div>
              <div class="input-wrapper password-wrapper">
                <input 
                  v-model="password" 
                  class="input" 
                  :class="{ 'input--error': errors.password, 'input--with-button': true }"
                  :type="showPassword ? 'text' : 'password'" 
                  placeholder="Минимум 6 символов, буквы и цифры"
                  maxlength="50"
                  @blur="handleBlur('password', password)"
                />
                <button
                  type="button"
                  class="password-toggle"
                  @click="togglePasswordVisibility"
                  :title="showPassword ? 'Скрыть пароль' : 'Показать пароль'"
                >
                  <svg v-if="!showPassword" width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M1 12C1 12 5 4 12 4C19 4 23 12 23 12C23 12 19 20 12 20C5 20 1 12 1 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M9.88 9.88C9.3185 10.4415 9.00467 11.2046 9 12C9 13.6569 10.3431 15 12 15C12.7954 15.0047 13.5585 14.6915 14.12 14.13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M17.61 6.39C16.1059 5.24965 14.2644 4.64302 12.37 4.66C8.27 4.66 4.84 7.74 2.75 12C3.604 13.7204 4.821 15.2317 6.31 16.43" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M8.25 19.26C9.48448 19.9107 10.8372 20.2513 12.21 20.26C16.31 20.26 19.74 17.18 21.83 13C21.1699 11.655 20.3144 10.4147 19.29 9.32" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M2 2L22 22" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </button>
                <transition name="fade">
                  <div v-if="errors.password" class="error-tooltip error-tooltip--password">{{ errors.password }}</div>
                </transition>
              </div>
              <div class="hint">Пароль должен содержать минимум 6 символов, буквы и цифры</div>
            </div>

            <button 
              class="btn btn-primary btn-submit" 
              type="submit"
              :disabled="submitting"
            >
              {{ submitting ? 'Вход…' : 'Войти' }}
            </button>
          </form>

          <div class="register-link">
            Нет аккаунта? 
            <router-link to="/register" class="link">Зарегистрироваться</router-link>
          </div>
        </div>
      </div>
    </div>
    <div class="gradient-bg gradient-right"></div>
  </div>
</template>

<style scoped>
/* Общий контейнер с тремя слоями */
.login-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
  background: #f5f7fa;
}

/* Левый градиент */
.gradient-left {
  position: fixed;
  left: 0;
  top: 0;
  width: 25%;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  z-index: 0;
}

/* Правый градиент */
.gradient-right {
  position: fixed;
  right: 0;
  top: 0;
  width: 25%;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  z-index: 0;
}

/* Центральная светлая часть с формой */
.content-wrapper {
  position: relative;
  z-index: 1;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f5f7fa;
}

.page {
  width: 100%;
  max-width: 680px;
  margin: 0 auto;
  padding: 20px;
}

.form-card {
  max-width: 100%;
  margin: 0 auto;
  width: 100%;
  position: relative;
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  padding: 32px;
}

/* Адаптация для планшетов и десктопов */
@media (min-width: 768px) and (max-width: 1200px) {
  .gradient-left,
  .gradient-right {
    width: 15%;
  }
}

/* Для мобильных устройств убираем боковые градиенты */
@media (max-width: 767px) {
  .gradient-left,
  .gradient-right {
    display: none;
  }
  
  .content-wrapper {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  }
  
  .form-card {
    background: white;
  }
  
  .form-card {
    padding: 24px;
  }
}

.form-group {
  margin-bottom: 20px;
  position: relative;
}

.label {
  margin-bottom: 6px;
  font-weight: 500;
  font-size: 14px;
  color: #2d3748;
}

.input-wrapper {
  position: relative;
}

.password-wrapper {
  position: relative;
}

.input {
  padding: 10px 12px;
  font-size: 14px;
  width: 100%;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  transition: all 0.2s ease;
  background: white;
}

.input--with-button {
  padding-right: 40px;
}

.input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.input--error {
  border-color: #ef4444;
  background: rgba(239, 68, 68, 0.03);
}

.input--error:focus {
  border-color: #ef4444;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.15);
}

.password-toggle {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #718096;
  transition: color 0.2s ease;
  z-index: 2;
}

.password-toggle:hover {
  color: #667eea;
}

.password-toggle:focus {
  outline: none;
}

/* Стили для тултипа справа от инпута */
.error-tooltip {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: #ef4444;
  color: #fff;
  font-size: 11px;
  font-weight: 500;
  padding: 4px 8px;
  border-radius: 6px;
  text-align: center;
  white-space: nowrap;
  z-index: 2;
  animation: slideIn 0.15s ease;
  pointer-events: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

/* Стрелка тултипа слева */
.error-tooltip--right::before {
  content: '';
  position: absolute;
  left: -4px;
  top: 50%;
  transform: translateY(-50%);
  border: 4px solid transparent;
  border-right-color: #ef4444;
}

/* Специальный стиль для тултипа пароля - справа от кнопки */
.error-tooltip--password {
  right: 48px;
}

.error-tooltip--password::before {
  content: '';
  position: absolute;
  right: -4px;
  top: 50%;
  transform: translateY(-50%);
  border: 4px solid transparent;
  border-left-color: #ef4444;
  left: auto;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-50%) translateX(-4px);
  }
  to {
    opacity: 1;
    transform: translateY(-50%) translateX(0);
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.hint {
  font-size: 12px;
  color: #718096;
  margin-top: 4px;
  padding-left: 2px;
}

.btn-submit {
  margin-top: 8px;
  padding: 12px 16px;
  font-size: 15px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  font-weight: 600;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  width: 100%;
  border-radius: 10px;
  cursor: pointer;
}

.btn-submit:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-submit:active {
  transform: translateY(0);
}

.form-error {
  margin: 0 0 16px 0;
  padding: 12px 14px;
  border-radius: 10px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.35);
  color: #b91c1c;
  font-size: 14px;
}

.btn-submit:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.register-link {
  margin-top: 20px;
  text-align: center;
  font-size: 14px;
  color: #718096;
}

.link {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s ease;
}

.link:hover {
  color: #764ba2;
  text-decoration: underline;
}

/* Адаптив для мобильных устройств */
@media (max-width: 768px) {
  .page {
    padding: 16px;
  }
  
  .form-card {
    border-radius: 16px;
    padding: 20px;
  }
  
  .error-tooltip {
    font-size: 10px;
    padding: 3px 6px;
    white-space: normal;
    word-break: break-word;
    max-width: 150px;
    text-align: left;
  }
  
  .error-tooltip--password {
    right: 44px;
  }
  
  .btn-submit:hover {
    transform: none;
  }
  
  .register-link {
    font-size: 13px;
  }
}
</style>
<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useNotificationsStore } from '../stores/notifications'
import { ROLE_LABEL, type Role } from '../types/roles'
import { useStudentsStore } from '../stores/students'
import { useScheduleStore } from '../stores/schedule'
import { registerUser } from '../api/auth'
import { toApiError } from '../api/http'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const notifications = useNotificationsStore()
const students = useStudentsStore()
const schedule = useScheduleStore()

const appName = import.meta.env.VITE_APP_NAME ?? '4tutor'

const selectedRole = ref<Role>('tutor')
const name = ref('')
const surname = ref('')
const email = ref('')
const password = ref('')
const subject = ref('')
const showPassword = ref(false)
const submitting = ref(false)
const formError = ref('')

// Валидация
const errors = ref<{
  name?: string
  surname?: string
  email?: string
  password?: string
  subject?: string
}>({})

const popularSubjects = [
  'Математика',
  'Русский язык',
  'Английский язык',
  'Физика',
  'Информатика',
  'Химия',
  'Биология',
  'История',
  'Обществознание',
  'Литература',
]

// Определяем тип для правил валидации
type ValidationRule = {
  min: number
  max: number
  required: boolean
  pattern?: RegExp
}

// Правила валидации
const validationRules: Record<'name' | 'surname' | 'email' | 'password' | 'subject', ValidationRule> = {
  name: { min: 2, max: 50, required: true, pattern: /^[\p{L}\p{M}\s'-]+$/u },
  surname: { min: 2, max: 50, required: true, pattern: /^[\p{L}\p{M}\s'-]+$/u },
  email: { min: 5, max: 100, required: true, pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/ },
  password: { 
    min: 8, 
    max: 50, 
    required: true, 
    pattern: /^(?=.*[A-Za-zА-Яа-яЁё])(?=.*\d)[A-Za-zА-Яа-яЁё\d@$!%*#?&]{8,}$/ 
  },
  subject: { min: 2, max: 100, required: true },
}

function validateField(field: 'name' | 'surname' | 'email' | 'password' | 'subject', value: string): string | undefined {
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
      return 'Только буквы и пробелы'
    }
  }
  
  return undefined
}

function handleBlur(field: 'name' | 'surname' | 'email' | 'password' | 'subject', value: string) {
  // Автоматически убираем пробелы по краям при потере фокуса
  if (field === 'name') name.value = value.trim()
  if (field === 'surname') surname.value = value.trim()
  if (field === 'email') email.value = value.trim()
  if (field === 'password') password.value = value.trim()
  
  errors.value[field] = validateField(field, value)
}

function validateAll(): boolean {
  const newErrors: typeof errors.value = {}
  
  newErrors.name = validateField('name', name.value)
  newErrors.surname = validateField('surname', surname.value)
  newErrors.email = validateField('email', email.value)
  newErrors.password = validateField('password', password.value)
  
  // Валидация предмета только для тьютора
  if (selectedRole.value === 'tutor') {
    newErrors.subject = validateField('subject', subject.value)
  }
  
  errors.value = newErrors
  return !Object.values(newErrors).some(Boolean)
}

const redirectTo = () => {
  const value = route.query.redirect
  if (typeof value === 'string') return value
  return null
}

async function submit() {
  if (!validateAll()) return
  formError.value = ''
  submitting.value = true

  const cleanName = name.value.trim()
  const cleanSurname = surname.value.trim()
  const cleanEmail = email.value.trim()
  const cleanPassword = password.value
  const cleanSubject = subject.value.trim()

  if (selectedRole.value === 'tutor' && cleanSubject) {
    if (typeof sessionStorage !== 'undefined') {
      sessionStorage.setItem('user_subject', cleanSubject)
    }
  } else {
    if (typeof sessionStorage !== 'undefined') {
      sessionStorage.removeItem('user_subject')
    }
  }

  try {
    await registerUser({
      email: cleanEmail,
      first_name: cleanName,
      last_name: cleanSurname,
      password: cleanPassword,
      role: selectedRole.value,
    })
    await auth.loginWithPassword(cleanEmail, cleanPassword)
    const role = auth.role
    if (!role) {
      formError.value = 'Не удалось определить роль пользователя'
      return
    }
    notifications.seedForRole(role)
    students.seedForRole()
    schedule.seedForRole()

    const target = redirectTo() ?? `/app/${role}`
    await router.push(target)
  } catch (err) {
    formError.value = toApiError(err).message
  } finally {
    submitting.value = false
  }
}

function togglePasswordVisibility() {
  showPassword.value = !showPassword.value
}
</script>

<template>
  <div class="register-wrapper">
    <div class="gradient-bg gradient-left"></div>
    <div class="content-wrapper">
      <div class="page">
        <div class="card form-card">
          <div class="row">
            <div>
              <div class="page-title" style="margin-bottom: 4px;">{{ appName }}</div>
              <div class="muted" style="font-weight: 700;">
                Регистрация
              </div>
            </div>
            <button class="btn" type="button" @click="$router.push('/login')">
              Уже есть аккаунт
            </button>
          </div>
        </div>

        <div class="card form-card">
          <h2 class="card-title">Выберите роль</h2>
          <div class="grid grid-cols-2" style="margin: 10px 0 14px 0;">
            <button
              type="button"
              class="btn role-btn"
              :class="{ 'role-btn--active': selectedRole === 'student' }"
              @click="selectedRole = 'student'"
            >
              {{ ROLE_LABEL.student }}
            </button>
            <button
              type="button"
              class="btn role-btn"
              :class="{ 'role-btn--active': selectedRole === 'tutor' }"
              @click="selectedRole = 'tutor'"
            >
              {{ ROLE_LABEL.tutor }}
            </button>
          </div>

          <div v-if="formError" class="form-error" role="alert">{{ formError }}</div>

          <form class="form" @submit.prevent="submit">
            <!-- Имя -->
            <div class="form-group">
              <div class="label">Имя</div>
              <div class="input-wrapper">
                <input 
                  v-model="name" 
                  class="input" 
                  :class="{ 'input--error': errors.name }"
                  type="text" 
                  placeholder="Например, Анна"
                  maxlength="50"
                  @blur="handleBlur('name', name)"
                />
                <transition name="fade">
                  <div v-if="errors.name" class="error-tooltip error-tooltip--right">{{ errors.name }}</div>
                </transition>
              </div>
            </div>

            <!-- Фамилия -->
            <div class="form-group">
              <div class="label">Фамилия</div>
              <div class="input-wrapper">
                <input 
                  v-model="surname" 
                  class="input" 
                  :class="{ 'input--error': errors.surname }"
                  type="text" 
                  placeholder="Например, Иванова"
                  maxlength="50"
                  @blur="handleBlur('surname', surname)"
                />
                <transition name="fade">
                  <div v-if="errors.surname" class="error-tooltip error-tooltip--right">{{ errors.surname }}</div>
                </transition>
              </div>
            </div>

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
                  placeholder="Минимум 8 символов, буквы и цифры"
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
              <div class="hint">Пароль должен содержать минимум 8 символов, буквы и цифры</div>
            </div>

            <!-- Предмет (только для тьютора) -->
            <div v-if="selectedRole === 'tutor'" class="form-group">
              <div class="label">Предмет преподавания</div>
              <div class="input-wrapper">
                <input 
                  v-model="subject" 
                  class="input" 
                  :class="{ 'input--error': errors.subject }"
                  list="subjects-list"
                  type="text" 
                  placeholder="Начните вводить или выберите из списка"
                  maxlength="100"
                  @blur="handleBlur('subject', subject)"
                />
                <datalist id="subjects-list">
                  <option v-for="subj in popularSubjects" :key="subj" :value="subj" />
                </datalist>
                <transition name="fade">
                  <div v-if="errors.subject" class="error-tooltip error-tooltip--right">{{ errors.subject }}</div>
                </transition>
              </div>
              <div class="hint">Можно выбрать из списка или ввести свой вариант</div>
            </div>

            <button 
              class="btn btn-primary btn-submit" 
              type="submit"
              :disabled="submitting"
            >
              {{ submitting ? 'Создание…' : 'Создать аккаунт' }}
            </button>
          </form>
        </div>
      </div>
    </div>
    <div class="gradient-bg gradient-right"></div>
  </div>
</template>

<style scoped>
/* Общий контейнер с тремя слоями */
.register-wrapper {
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
}

.role-btn {
  transition: all 0.2s ease;
  padding: 10px 16px;
  font-weight: 500;
}

.role-btn--active {
  border-color: rgba(30, 58, 138, 0.6);
  background: rgba(30, 58, 138, 0.04);
  box-shadow: 0 0 0 3px rgba(30, 58, 138, 0.1);
}

.form-group {
  margin-bottom: 2px;
  position: relative;
}

.label {
  margin-bottom: 6px;
  font-weight: 500;
  font-size: 14px;
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
  color: rgb(0, 0, 0);
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

/* Стили для кнопок ролей */
.btn {
  padding: 8px 16px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background: white;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn:hover {
  border-color: #cbd5e0;
  background: #f7fafc;
}

/* Адаптив для мобильных устройств */
@media (max-width: 768px) {
  .page {
    padding: 16px;
  }
  
  .form-card {
    border-radius: 16px;
  }
  
  .row {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
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
}
</style>
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getTutorDashboard } from '@/api/dashboard'
import type { TutorDashboardData } from '@/api/dashboard'

const router = useRouter()
const dashboardData = ref<TutorDashboardData | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const isOverdue = (deadline: string) => new Date(deadline) < new Date()

// Вычисляемые проценты для мини-баров в статистике
const statsProgress = computed(() => {
  if (!dashboardData.value) return null
  const s = dashboardData.value.assignment_stats
  const total = s.total_assignments || 1
  return {
    active: Math.round((s.active_assignments / total) * 100),
    pending: Math.round((s.submitted_pending / total) * 100),
    graded: Math.round((s.graded_count / total) * 100)
  }
})

onMounted(async () => {
  try {
    dashboardData.value = await getTutorDashboard()
  } catch (e) {
    error.value = 'Не удалось загрузить данные дашборда'
    console.error(e)
  } finally {
    loading.value = false
  }
})

const goToAssignment = (id: number) => router.push(`/app/tutor/assignments/${id}`)
const goToStudents = () => router.push('/app/tutor/students')
const createNewAssignment = () => router.push('/app/tutor/assignments/create')
</script>

<template>
  <div class="dashboard">
    <!-- Заголовок -->
    <header class="dashboard-header">
      <h1 class="page-title">Дашборд репетитора</h1>
      <p class="page-subtitle">Быстрый обзор учеников, заданий и дедлайнов</p>
    </header>

    <!-- Состояния загрузки/ошибки -->
    <div v-if="loading" class="status-message">Загрузка...</div>
    <div v-else-if="error" class="status-message error">{{ error }}</div>

    <div v-else-if="dashboardData" class="dashboard-content">
      <!-- Секция 1: Крупные плитки статистики -->
      <section class="stats-row">
        <div class="stat-tile">
          <div class="stat-number">{{ dashboardData.assignment_stats.total_assignments }}</div>
          <div class="stat-label">Всего заданий</div>
          <div class="mini-bar"><span class="fill" style="width:100%"></span></div>
        </div>
        <div class="stat-tile">
          <div class="stat-number">{{ dashboardData.assignment_stats.active_assignments }}</div>
          <div class="stat-label">Активных</div>
          <div class="mini-bar">
            <span class="fill" :style="{ width: statsProgress?.active + '%' }"></span>
          </div>
        </div>
        <div class="stat-tile">
          <div class="stat-number">{{ dashboardData.assignment_stats.submitted_pending }}</div>
          <div class="stat-label">На проверке</div>
          <div class="mini-bar warning">
            <span class="fill" :style="{ width: statsProgress?.pending + '%' }"></span>
          </div>
        </div>
        <div class="stat-tile">
          <div class="stat-number">{{ dashboardData.assignment_stats.graded_count }}</div>
          <div class="stat-label">Проверено</div>
          <div class="mini-bar success">
            <span class="fill" :style="{ width: statsProgress?.graded + '%' }"></span>
          </div>
        </div>
      </section>

      <!-- Секция 2: Сетка с разными весами блоков -->
      <div class="importance-grid">
        <!-- Ближайшие дедлайны (широкий) -->
        <section class="card card--deadlines span-2">
          <div class="card-header">
            <h2 class="card-title">📅 Ближайшие дедлайны</h2>
          </div>
          <div v-if="dashboardData.upcoming_deadlines.length" class="card-body">
            <ul class="deadline-list">
              <li
                v-for="item in dashboardData.upcoming_deadlines"
                :key="item.id"
                class="deadline-item"
                :class="{ overdue: isOverdue(item.deadline) }"
                @click="goToAssignment(item.id)"
              >
                <div class="item-info">
                  <span class="assignment-name">{{ item.assignment_title }}</span>
                  <span class="student-name">{{ item.student_name }}</span>
                </div>
                <div class="item-date">
                  <span class="date" :class="{ 'text-danger': isOverdue(item.deadline) }">
                    {{ formatDate(item.deadline) }}
                  </span>
                </div>
              </li>
            </ul>
          </div>
          <div v-else class="empty-state">Все задания вовремя сданы</div>
        </section>

        <!-- Последние задания (компактный) -->
        <section class="card card--recent span-1">
          <div class="card-header">
            <h2 class="card-title">📝 Последние</h2>
            <button class="btn btn-primary btn-sm" @click="createNewAssignment">+</button>
          </div>
          <div v-if="dashboardData.recent_assignments.length" class="card-body">
            <ul class="compact-list">
              <li
                v-for="item in dashboardData.recent_assignments"
                :key="item.id"
                class="compact-item"
                @click="goToAssignment(item.id)"
              >
                <span class="title">{{ item.title }}</span>
                <span class="meta">{{ formatDate(item.created_at) }}</span>
              </li>
            </ul>
          </div>
          <div v-else class="empty-state">Нет заданий</div>
        </section>

        <!-- Требуют внимания (широкий) -->
        <section class="card card--attention span-2">
          <div class="card-header">
            <h2 class="card-title">⚠️ Требуют внимания</h2>
          </div>
          <div class="attention-blocks">
            <div class="attention-group">
              <h3 class="group-title">Ожидают оценки ({{ dashboardData.needs_attention.submitted_pending_count }})</h3>
              <ul v-if="dashboardData.needs_attention.submitted_pending.length" class="attention-list">
                <li
                  v-for="item in dashboardData.needs_attention.submitted_pending"
                  :key="item.id"
                  class="attention-item"
                >
                  <span>{{ item.assignment_title }} — {{ item.student_name }}</span>
                  <button class="btn btn-primary btn-sm" @click="goToAssignment(item.id)">Оценить</button>
                </li>
              </ul>
              <div v-else class="ok-message">Всё проверено ✓</div>
            </div>
            <div class="attention-group overdue-group">
              <h3 class="group-title">Просроченные ({{ dashboardData.needs_attention.overdue_count }})</h3>
              <ul v-if="dashboardData.needs_attention.overdue.length" class="attention-list">
                <li
                  v-for="item in dashboardData.needs_attention.overdue"
                  :key="item.id"
                  class="attention-item overdue-item"
                >
                  <span>
                    {{ item.assignment_title }} — {{ item.student_name }}
                    <span class="overdue-date">{{ formatDate(item.deadline) }}</span>
                  </span>
                  <button class="btn btn-danger btn-sm" @click="goToAssignment(item.id)">Открыть</button>
                </li>
              </ul>
              <div v-else class="ok-message">Просрочек нет ✓</div>
            </div>
          </div>
        </section>

        <!-- Активные ученики (компактный) -->
        <section class="card card--students span-1">
          <div class="card-header">
            <h2 class="card-title">👥 Ученики</h2>
            <button class="btn btn-outline btn-sm" @click="goToStudents">Все</button>
          </div>
          <div v-if="dashboardData.active_students.length" class="card-body">
            <ul class="compact-list">
              <li
                v-for="student in dashboardData.active_students"
                :key="student.id"
                class="compact-item"
              >
                <span class="title">{{ student.first_name }} {{ student.last_name }}</span>
                <span v-if="student.pending_assignments_count" class="badge-pending">
                  {{ student.pending_assignments_count }} не сдано
                </span>
                <span v-else class="meta">Всё сдано</span>
              </li>
            </ul>
          </div>
          <div v-else class="empty-state">Нет учеников</div>
        </section>
      </div>
    </div>
  </div>
</template>

<style scoped>
:root {
  --color-bg: #f5f7fc;
  --color-surface: #ffffff;
  --color-primary: #4361ee;
  --color-primary-light: #eef1ff;
  --color-danger: #f72585;
  --color-danger-bg: #fff0f5;
  --color-warning: #f8961e;
  --color-success: #06d6a0;
  --color-text: #1e293b;
  --color-text-muted: #64748b;
  --color-border: #e9eef2;
  --radius: 16px;
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.04);
  --shadow-md: 0 4px 12px rgba(0,0,0,0.06);
  --transition: 0.2s ease;
}

/* ----- Базовые стили страницы ----- */
.dashboard {
  max-width: 1280px;
  margin: 0 auto;
  padding: 28px 24px;
  background: var(--color-bg);
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  color: var(--color-text);
  min-height: 100vh;
}
.dashboard-header {
  margin-bottom: 32px;
}
.page-title {
  font-size: 30px;
  font-weight: 700;
  margin: 0 0 6px;
  letter-spacing: -0.5px;
}
.page-subtitle {
  color: var(--color-text-muted);
  font-size: 15px;
  margin: 0;
}

/* ----- Сообщения состояния ----- */
.status-message {
  text-align: center;
  padding: 60px 20px;
  font-size: 16px;
  color: var(--color-text-muted);
}
.status-message.error {
  color: var(--color-danger);
}

/* ----- Строка со статистикой ----- */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 28px;
}
.stat-tile {
  background: var(--color-surface);
  border-radius: var(--radius);
  padding: 22px 20px;
  box-shadow: var(--shadow-md);
  transition: transform var(--transition), box-shadow var(--transition);
  text-align: center;
}
.stat-tile:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.08);
}
.stat-number {
  font-size: 42px;
  font-weight: 800;
  line-height: 1;
  color: var(--color-primary);
  margin-bottom: 8px;
}
.stat-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
}
.mini-bar {
  height: 4px;
  background: #e9eef2;
  border-radius: 4px;
  overflow: hidden;
  margin-top: auto;
}
.mini-bar .fill {
  display: block;
  height: 100%;
  background: var(--color-primary);
  border-radius: 4px;
  transition: width 0.6s ease;
}
.mini-bar.warning .fill {
  background: var(--color-warning);
}
.mini-bar.success .fill {
  background: var(--color-success);
}

/* ----- Сетка с весами важности ----- */
.importance-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}
.span-2 {
  grid-column: span 2;
}
.span-1 {
  grid-column: span 1;
}

/* ----- Карточки ----- */
.card {
  background: var(--color-surface);
  border-radius: var(--radius);
  padding: 24px;
  box-shadow: var(--shadow-md);
  transition: box-shadow var(--transition);
  display: flex;
  flex-direction: column;
}
.card:hover {
  box-shadow: 0 6px 18px rgba(0,0,0,0.08);
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.card-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}
.card-body {
  flex: 1;
}

/* ----- Дедлайны ----- */
.deadline-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.deadline-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid var(--color-border);
  cursor: pointer;
  transition: background var(--transition);
}
.deadline-item:last-child {
  border-bottom: none;
}
.deadline-item:hover {
  background: #f8fafd;
  margin: 0 -12px;
  padding-left: 12px;
  padding-right: 12px;
  border-radius: 8px;
}
.deadline-item.overdue {
  background: var(--color-danger-bg);
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 4px;
  border: none;
}
.deadline-item.overdue:hover {
  background: #ffe0e8;
}
.item-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.assignment-name {
  font-weight: 600;
}
.student-name {
  font-size: 13px;
  color: var(--color-text-muted);
}
.item-date .date {
  font-size: 13px;
  color: var(--color-text-muted);
}
.text-danger {
  color: var(--color-danger) !important;
  font-weight: 500;
}

/* ----- Последние задания и Ученики (компактный список) ----- */
.compact-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.compact-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid var(--color-border);
  cursor: pointer;
  transition: background var(--transition);
}
.compact-item:last-child {
  border-bottom: none;
}
.compact-item:hover {
  background: #f8fafd;
  margin: 0 -8px;
  padding-left: 8px;
  padding-right: 8px;
  border-radius: 8px;
}
.compact-item .title {
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 70%;
}
.compact-item .meta,
.compact-item .badge-pending {
  font-size: 12px;
  color: var(--color-text-muted);
  white-space: nowrap;
}
.badge-pending {
  color: var(--color-danger);
  font-weight: 500;
}

/* ----- Требуют внимания ----- */
.attention-blocks {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.attention-group {
  flex: 1;
}
.group-title {
  font-size: 15px;
  font-weight: 600;
  margin: 0 0 12px;
  color: var(--color-text);
}
.overdue-group .group-title {
  color: var(--color-danger);
}
.attention-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.attention-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px dashed var(--color-border);
}
.attention-item:last-child {
  border-bottom: none;
}
.overdue-item {
  background: var(--color-danger-bg);
  padding: 10px 12px;
  border-radius: 8px;
  margin-bottom: 8px;
  border: none;
}
.overdue-date {
  font-size: 12px;
  color: var(--color-danger);
  margin-left: 8px;
  font-weight: 500;
}
.ok-message {
  font-size: 13px;
  color: var(--color-success);
  padding: 4px 0;
}

/* ----- Кнопки ----- */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 8px 16px;
  border-radius: 10px;
  font-weight: 500;
  font-size: 13px;
  border: none;
  cursor: pointer;
  transition: all var(--transition);
  white-space: nowrap;
}
.btn-sm {
  padding: 5px 12px;
  font-size: 12px;
}
.btn-primary {
  background: var(--color-primary);
  color: white;
}
.btn-primary:hover {
  background: #3050d0;
}
.btn-outline {
  background: transparent;
  border: 1px solid var(--color-primary);
  color: var(--color-primary);
}
.btn-outline:hover {
  background: var(--color-primary-light);
}
.btn-danger {
  background: var(--color-danger);
  color: white;
}
.btn-danger:hover {
  background: #d91e6c;
}

/* ----- Пустые состояния ----- */
.empty-state {
  text-align: center;
  padding: 20px;
  color: var(--color-text-muted);
  font-size: 14px;
}

/* ----- Адаптив ----- */
@media (max-width: 1024px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }
  .importance-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .span-2 {
    grid-column: span 2; /* на планшетах широкие блоки занимают всю ширину */
  }
  .span-1 {
    grid-column: span 1;
  }
}
@media (max-width: 640px) {
  .dashboard {
    padding: 16px;
  }
  .stats-row {
    grid-template-columns: 1fr;
  }
  .importance-grid {
    grid-template-columns: 1fr;
  }
  .span-2,
  .span-1 {
    grid-column: span 1;
  }
}
</style>
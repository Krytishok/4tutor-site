<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  ClipboardList,
  Flame,
  Clock3,
  CheckCircle2,
  AlertTriangle,
  Plus,
  ArrowRight
} from 'lucide-vue-next'

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
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const isOverdue = (deadline: string) => {
  return new Date(deadline) < new Date()
}

const stats = computed(() => {
  if (!dashboardData.value) return null

  const s = dashboardData.value.assignment_stats
  const total = s.total_assignments || 1

  return [
    {
      label: 'Всего заданий',
      value: s.total_assignments,
      progress: 100,
      icon: ClipboardList,
      color: 'primary'
    },
    {
      label: 'Активных',
      value: s.active_assignments,
      progress: Math.round((s.active_assignments / total) * 100),
      icon: Flame,
      color: 'orange'
    },
    {
      label: 'На проверке',
      value: s.submitted_pending,
      progress: Math.round((s.submitted_pending / total) * 100),
      icon: Clock3,
      color: 'warning'
    },
    {
      label: 'Проверено',
      value: s.graded_count,
      progress: Math.round((s.graded_count / total) * 100),
      icon: CheckCircle2,
      color: 'success'
    }
  ]
})

onMounted(async () => {
  try {
    dashboardData.value = await getTutorDashboard()
  } catch (e) {
    error.value = 'Не удалось загрузить дашборд'
    console.error(e)
  } finally {
    loading.value = false
  }
})

const goToAssignment = (id: number) => {
  router.push(`/app/tutor/assignments/${id}`)
}

const goToStudents = () => {
  router.push('/app/tutor/students')
}

const createNewAssignment = () => {
  router.push('/app/tutor/assignments')
}
</script>

<template>
  <div class="dashboard">
    <!-- Hero -->
    <header class="dashboard-hero">
      <div class="hero-content">
        <div class="hero-badge">
          <span class="hero-dot"></span>
          Панель преподавателя
        </div>

        <h1 class="hero-title">
          Добро пожаловать обратно
        </h1>

        <p class="hero-subtitle">
          Следите за дедлайнами, проверяйте задания и контролируйте прогресс учеников.
        </p>
      </div>

      <button
        class="btn btn-primary hero-btn"
        @click="createNewAssignment"
      >
        <Plus :size="18" />
        Новое задание
      </button>
    </header>

    <!-- Loading -->
    <div v-if="loading" class="skeleton-grid">
      <div class="skeleton-card" v-for="i in 4" :key="i"></div>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="error-state">
      {{ error }}
    </div>

    <!-- Content -->
    <div v-else-if="dashboardData && stats">
      <!-- Stats -->
      <section class="stats-grid">
        <div
          v-for="item in stats"
          :key="item.label"
          class="stat-card"
        >
          <div class="stat-top">
            <div class="stat-icon" :class="item.color">
              <component :is="item.icon" :size="22" />
            </div>

            <div class="stat-progress">
              {{ item.progress }}%
            </div>
          </div>

          <div class="stat-value">
            {{ item.value }}
          </div>

          <div class="stat-label">
            {{ item.label }}
          </div>

          <div class="progress-bar">
            <div
              class="progress-fill"
              :class="item.color"
              :style="{ width: item.progress + '%' }"
            ></div>
          </div>
        </div>
      </section>

      <!-- Main Layout -->
      <section class="main-grid">
        <!-- LEFT -->
        <div class="left-column">
          <!-- Deadlines -->
          <div class="dashboard-card primary-card">
            <div class="card-header">
              <div>
                <h2>Ближайшие дедлайны</h2>
                <p>Требуют внимания в ближайшее время</p>
              </div>
            </div>

            <div
              v-if="dashboardData.upcoming_deadlines.length"
              class="deadline-list"
            >
              <div
                v-for="item in dashboardData.upcoming_deadlines"
                :key="item.id"
                class="deadline-item"
                :class="{ overdue: isOverdue(item.deadline) }"
                @click="goToAssignment(item.id)"
              >
                <div class="deadline-main">
                  <div class="deadline-title">
                    {{ item.assignment_title }}
                  </div>

                  <div class="deadline-student">
                    {{ item.student_name }}
                  </div>
                </div>

                <div class="deadline-side">
                  <div
                    class="deadline-date"
                    :class="{ overdue: isOverdue(item.deadline) }"
                  >
                    {{ formatDate(item.deadline) }}
                  </div>

                  <ArrowRight :size="16" />
                </div>
              </div>
            </div>

            <div v-else class="empty-state">
              Всё отлично — ближайших дедлайнов нет.
            </div>
          </div>

          <!-- Attention -->
          <div class="dashboard-card primary-card">
            <div class="card-header">
              <div>
                <h2>Требуют внимания</h2>
                <p>Проверка работ и просроченные задания</p>
              </div>
            </div>

            <!-- Pending -->
            <div class="attention-block warning">
              <div class="attention-header">
                <div class="attention-title">
                  <Clock3 :size="18" />
                  Ожидают оценки
                </div>

                <div class="attention-count">
                  {{ dashboardData.needs_attention.submitted_pending_count }}
                </div>
              </div>

              <div
                v-if="dashboardData.needs_attention.submitted_pending.length"
                class="attention-list"
              >
                <div
                  v-for="item in dashboardData.needs_attention.submitted_pending"
                  :key="item.id"
                  class="attention-item"
                >
                  <div>
                    <div class="attention-item-title">
                      {{ item.assignment_title }}
                    </div>

                    <div class="attention-item-subtitle">
                      {{ item.student_name }}
                    </div>
                  </div>

                  <button
                    class="btn btn-sm btn-primary"
                    @click.stop="goToAssignment(item.id)"
                  >
                    Проверить
                  </button>
                </div>
              </div>

              <div v-else class="ok-state">
                Всё проверено
              </div>
            </div>

            <!-- Overdue -->
            <div class="attention-block danger">
              <div class="attention-header">
                <div class="attention-title">
                  <AlertTriangle :size="18" />
                  Просрочено
                </div>

                <div class="attention-count">
                  {{ dashboardData.needs_attention.overdue_count }}
                </div>
              </div>

              <div
                v-if="dashboardData.needs_attention.overdue.length"
                class="attention-list"
              >
                <div
                  v-for="item in dashboardData.needs_attention.overdue"
                  :key="item.id"
                  class="attention-item"
                >
                  <div>
                    <div class="attention-item-title">
                      {{ item.assignment_title }}
                    </div>

                    <div class="attention-item-subtitle">
                      {{ item.student_name }}
                    </div>
                  </div>

                  <button
                    class="btn btn-sm danger-btn"
                    @click.stop="goToAssignment(item.id)"
                  >
                    Открыть
                  </button>
                </div>
              </div>

              <div v-else class="ok-state">
                Просрочек нет
              </div>
            </div>
          </div>
        </div>

        <!-- RIGHT -->
        <div class="right-column">
          <!-- Recent -->
          <div class="dashboard-card secondary-card">
            <div class="card-header">
              <div>
                <h2>Последние задания</h2>
                <p>Недавно созданные задания</p>
              </div>

              <button
                class="btn btn-outline btn-sm"
                @click="createNewAssignment"
              >
                Добавить
              </button>
            </div>

            <div
              v-if="dashboardData.recent_assignments.length"
              class="compact-list"
            >
              <div
                v-for="item in dashboardData.recent_assignments"
                :key="item.id"
                class="compact-item"
                @click="goToAssignment(item.id)"
              >
                <div>
                  <div class="compact-title">
                    {{ item.title }}
                  </div>

                  <div class="compact-meta">
                    {{ formatDate(item.created_at) }}
                  </div>
                </div>

                <ArrowRight :size="16" />
              </div>
            </div>

            <div v-else class="empty-state small">
              Пока нет заданий
            </div>
          </div>

          <!-- Students -->
          <div class="dashboard-card secondary-card">
            <div class="card-header">
              <div>
                <h2>Активные ученики</h2>
                <p>Текущая активность учеников</p>
              </div>

              <button
                class="btn btn-outline btn-sm"
                @click="goToStudents"
              >
                Все
              </button>
            </div>

            <div
              v-if="dashboardData.active_students.length"
              class="compact-list"
            >
              <div
                v-for="student in dashboardData.active_students"
                :key="student.id"
                class="compact-item no-hover"
              >
                <div class="student-row">
                  <div class="student-avatar">
                    {{ student.first_name[0] }}
                  </div>

                  <div>
                    <div class="compact-title">
                      {{ student.first_name }}
                      {{ student.last_name }}
                    </div>

                    <div class="compact-meta">
                      Активный ученик
                    </div>
                  </div>
                </div>

                <div
                  v-if="student.pending_assignments_count"
                  class="badge pending"
                >
                  {{ student.pending_assignments_count }}
                </div>

                <div v-else class="badge success">
                  ✓
                </div>
              </div>
            </div>

            <div v-else class="empty-state small">
              Пока нет учеников
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  padding: 32px;
  max-width: 1480px;
  margin: 0 auto;
  min-height: 100vh;

  background:
    radial-gradient(
      circle at top left,
      rgba(30,58,138,0.04),
      transparent 28%
    ),
    var(--bg);
}

/* HERO */

.dashboard-hero {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;

  padding: 32px;
  margin-bottom: 32px;

  background:
    linear-gradient(
      135deg,
      rgba(30,58,138,0.08),
      rgba(30,58,138,0.02)
    );

  border: 1px solid rgba(30,58,138,0.08);
  border-radius: 28px;
}

.hero-content {
  max-width: 720px;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;

  margin-bottom: 16px;

  font-size: 13px;
  font-weight: 700;

  color: var(--primary);
}

.hero-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: var(--primary);
}

.hero-title {
  margin: 0;

  font-size: 38px;
  line-height: 1.05;
  letter-spacing: -0.05em;

  color: var(--text);
}

.hero-subtitle {
  margin: 14px 0 0;

  max-width: 620px;

  font-size: 16px;
  line-height: 1.65;

  color: var(--muted);
}

.hero-btn {
  height: 48px;
  padding-inline: 18px;
  border-radius: 14px;
}

/* STATS */

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 20px;

  margin-bottom: 28px;
}

.stat-card {
  padding: 22px;

  background: rgba(255,255,255,0.9);

  backdrop-filter: blur(12px);

  border: 1px solid rgba(255,255,255,0.8);
  border-radius: 24px;

  transition:
    transform .2s ease,
    box-shadow .2s ease,
    border-color .2s ease;
}

.stat-card:hover {
  transform: translateY(-3px);

  border-color: rgba(30,58,138,0.08);

  box-shadow:
    0 14px 40px rgba(15,23,42,0.06);
}

.stat-top {
  display: flex;
  align-items: center;
  justify-content: space-between;

  margin-bottom: 18px;
}

.stat-icon {
  width: 48px;
  height: 48px;

  border-radius: 16px;

  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon.primary {
  background: rgba(30,58,138,0.10);
  color: var(--primary);
}

.stat-icon.orange {
  background: rgba(249,115,22,0.10);
  color: #ea580c;
}

.stat-icon.warning {
  background: rgba(245,158,11,0.10);
  color: #d97706;
}

.stat-icon.success {
  background: rgba(16,185,129,0.10);
  color: var(--success);
}

.stat-progress {
  font-size: 13px;
  font-weight: 700;
  color: var(--muted);
}

.stat-value {
  font-size: 36px;
  line-height: 1;

  font-weight: 800;
  letter-spacing: -0.04em;

  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: var(--muted);

  margin-bottom: 18px;
}

.progress-bar {
  height: 7px;
  border-radius: 999px;
  overflow: hidden;

  background: #eef2f7;
}

.progress-fill {
  height: 100%;
  border-radius: inherit;

  transition: width .5s ease;
}

.progress-fill.primary {
  background: var(--primary);
}

.progress-fill.orange {
  background: #ea580c;
}

.progress-fill.warning {
  background: var(--reminder);
}

.progress-fill.success {
  background: var(--success);
}

/* MAIN GRID */

.main-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.6fr) minmax(320px, 420px);
  gap: 24px;
  align-items: start;
}

.left-column {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.right-column {
  position: sticky;
  top: 88px;

  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* CARDS */

.dashboard-card {
  border-radius: 26px;
  padding: 26px;

  border: 1px solid var(--border);
}

.primary-card {
  background: white;
}

.secondary-card {
  background: #fcfcfd;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;

  margin-bottom: 24px;
}

.card-header h2 {
  margin: 0 0 4px;

  font-size: 18px;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.card-header p {
  margin: 0;
  font-size: 14px;
  color: var(--muted);
}

/* DEADLINES */

.deadline-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.deadline-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;

  padding: 16px;

  border-radius: 18px;
  border: 1px solid transparent;

  cursor: pointer;

  transition: all .18s ease;
}

.deadline-item:hover {
  background: rgba(30,58,138,0.04);
  border-color: rgba(30,58,138,0.05);

  transform: translateX(2px);
}

.deadline-item.overdue {
  background: rgba(239,68,68,0.05);
}

.deadline-main {
  flex: 1;
}

.deadline-title {
  font-size: 15px;
  font-weight: 600;

  margin-bottom: 4px;
}

.deadline-student {
  font-size: 13px;
  color: var(--muted);
}

.deadline-side {
  display: flex;
  align-items: center;
  gap: 12px;

  color: var(--muted);
}

.deadline-date {
  font-size: 13px;
  font-weight: 600;
}

.deadline-date.overdue {
  color: var(--danger);
}

/* ATTENTION */

.attention-block {
  padding: 18px;
  border-radius: 20px;

  margin-bottom: 16px;
}

.attention-block.warning {
  background: rgba(245,158,11,0.08);
}

.attention-block.danger {
  background: rgba(239,68,68,0.08);
}

.attention-header {
  display: flex;
  align-items: center;
  justify-content: space-between;

  margin-bottom: 16px;
}

.attention-title {
  display: flex;
  align-items: center;
  gap: 10px;

  font-size: 15px;
  font-weight: 700;
}

.attention-count {
  min-width: 28px;
  height: 28px;

  border-radius: 999px;

  display: flex;
  align-items: center;
  justify-content: center;

  background: rgba(255,255,255,0.7);

  font-size: 13px;
  font-weight: 700;
}

.attention-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.attention-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;

  padding: 14px;

  background: rgba(255,255,255,0.7);

  border-radius: 14px;
}

.attention-item-title {
  font-size: 14px;
  font-weight: 600;

  margin-bottom: 4px;
}

.attention-item-subtitle {
  font-size: 13px;
  color: var(--muted);
}

/* COMPACT LIST */

.compact-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.compact-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;

  padding: 14px;

  border-radius: 16px;
  border: 1px solid transparent;

  cursor: pointer;

  transition: all .18s ease;
}

.compact-item:hover {
  background: rgba(30,58,138,0.04);
  border-color: rgba(30,58,138,0.05);

  transform: translateX(2px);
}

.compact-item.no-hover {
  cursor: default;
}

.compact-item.no-hover:hover {
  transform: none;
}

.compact-title {
  font-size: 14px;
  font-weight: 600;

  margin-bottom: 4px;
}

.compact-meta {
  font-size: 13px;
  color: var(--muted);
}

/* STUDENTS */

.student-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.student-avatar {
  width: 38px;
  height: 38px;

  border-radius: 12px;

  display: flex;
  align-items: center;
  justify-content: center;

  background: rgba(30,58,138,0.08);

  color: var(--primary);

  font-size: 14px;
  font-weight: 800;
}

/* BADGES */

.badge {
  min-width: 28px;
  height: 28px;

  padding-inline: 10px;

  border-radius: 999px;

  display: flex;
  align-items: center;
  justify-content: center;

  font-size: 12px;
  font-weight: 700;
}

.badge.pending {
  background: rgba(245,158,11,0.12);
  color: #b45309;
}

.badge.success {
  background: rgba(16,185,129,0.12);
  color: var(--success);
}

/* STATES */

.empty-state {
  padding: 40px 20px;

  text-align: center;

  color: var(--muted);
  font-size: 14px;
}

.empty-state.small {
  padding: 24px 12px;
}

.ok-state {
  padding: 10px 0;

  font-size: 14px;
  font-weight: 600;

  color: var(--success);
}

.error-state {
  padding: 24px;

  border-radius: 18px;

  background: rgba(239,68,68,0.08);

  color: var(--danger);
}

/* BUTTONS */

.btn-sm {
  height: 36px;
  padding-inline: 14px;

  font-size: 13px;
}

.danger-btn {
  background: var(--danger);
  color: white;
  border-color: transparent;
}

.danger-btn:hover {
  opacity: 0.92;
}

/* SKELETON */

.skeleton-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 20px;
}

.skeleton-card {
  height: 160px;

  border-radius: 24px;

  background:
    linear-gradient(
      90deg,
      #f3f4f6 25%,
      #e5e7eb 37%,
      #f3f4f6 63%
    );

  background-size: 400% 100%;

  animation: shimmer 1.4s ease infinite;
}

@keyframes shimmer {
  0% {
    background-position: 100% 0;
  }

  100% {
    background-position: -100% 0;
  }
}

/* RESPONSIVE */

@media (max-width: 1180px) {
  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .main-grid {
    grid-template-columns: 1fr;
  }

  .right-column {
    position: static;
  }
}

@media (max-width: 768px) {
  .dashboard {
    padding: 18px;
  }

  .dashboard-hero {
    flex-direction: column;
    align-items: flex-start;

    padding: 24px;
  }

  .hero-title {
    font-size: 30px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .skeleton-grid {
    grid-template-columns: 1fr;
  }

  .dashboard-card {
    padding: 20px;
  }

  .deadline-item,
  .attention-item,
  .compact-item {
    padding: 14px;
  }

  .card-header {
    flex-direction: column;
  }
}
</style>
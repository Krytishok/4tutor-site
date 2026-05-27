<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

import {
  BookOpen,
  Trophy,
  BarChart3,
  GraduationCap,
  ArrowRight,
  CheckCircle2
} from 'lucide-vue-next'

import { getStudentDashboard } from '@/api/dashboard'
import type { StudentDashboardData } from '@/api/dashboard'

const router = useRouter()

const dashboardData = ref<StudentDashboardData | null>(null)
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

const getGradeVariant = (grade: number, maxGrade: number = 10) => {
  const percentage = (grade / maxGrade) * 100

  if (percentage >= 80) return 'success'
  if (percentage >= 60) return 'warning'

  return 'danger'
}

const stats = computed(() => {
  if (!dashboardData.value) return []

  return [
    {
      label: 'Всего заданий',
      value: dashboardData.value.stats.total_assignments,
      icon: BookOpen,
      color: 'primary'
    },
    {
      label: 'Выполнено',
      value: dashboardData.value.stats.completed_count,
      icon: CheckCircle2,
      color: 'success'
    },
    {
      label: 'Средний балл',
      value: dashboardData.value.stats.average_grade,
      icon: Trophy,
      color: 'warning'
    },
    {
      label: 'Прогресс',
      value: `${dashboardData.value.stats.progress_percentage}%`,
      icon: BarChart3,
      color: 'purple'
    }
  ]
})

onMounted(async () => {
  try {
    dashboardData.value = await getStudentDashboard()
  } catch (e) {
    error.value = 'Не удалось загрузить данные дашборда'
    console.error(e)
  } finally {
    loading.value = false
  }
})

const goToAssignment = (id: number) => {
  router.push(`/app/student/assignments/${id}`)
}

const goToAssignments = () => {
  router.push('/app/student/assignments')
}
</script>

<template>
  <div class="dashboard">
    <!-- HERO -->
    <header class="dashboard-hero">
      <div class="hero-content">
        <div class="hero-badge">
          <span class="hero-dot"></span>
          Личный кабинет ученика
        </div>

        <h1 class="hero-title">
          Ваш прогресс и задания
        </h1>

        <p class="hero-subtitle">
          Следите за дедлайнами, оценками и активностью по всем предметам.
        </p>
      </div>

      <button
        class="btn btn-primary hero-btn"
        @click="goToAssignments"
      >
        <BookOpen :size="18" />
        Все задания
      </button>
    </header>

    <!-- LOADING -->
    <div v-if="loading" class="skeleton-grid">
      <div
        v-for="i in 4"
        :key="i"
        class="skeleton-card"
      ></div>
    </div>

    <!-- ERROR -->
    <div v-else-if="error" class="error-state">
      {{ error }}
    </div>

    <!-- CONTENT -->
    <div v-else-if="dashboardData">
      <!-- STATS -->
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
          </div>

          <div class="stat-value">
            {{ item.value }}
          </div>

          <div class="stat-label">
            {{ item.label }}
          </div>
        </div>
      </section>

      <!-- MAIN GRID -->
      <section class="main-grid">
        <!-- LEFT -->
        <div class="left-column">
          <!-- ACTIVE ASSIGNMENTS -->
          <div class="dashboard-card primary-card">
            <div class="card-header">
              <div>
                <h2>Активные задания</h2>
                <p>Текущие задания с дедлайнами</p>
              </div>

              <button
                class="btn btn-outline btn-sm"
                @click="goToAssignments"
              >
                Все задания
              </button>
            </div>

            <div
              v-if="dashboardData.active_assignments.length"
              class="assignment-list"
            >
              <div
                v-for="item in dashboardData.active_assignments"
                :key="item.id"
                class="assignment-item"
                @click="goToAssignment(item.id)"
              >
                <div class="assignment-main">
                  <div class="assignment-title">
                    {{ item.assignment_title }}
                  </div>

                  <div class="assignment-meta">
                    <span>{{ item.tutor_name }}</span>

                    <span
                      v-if="item.subject"
                      class="subject-chip"
                    >
                      {{ item.subject }}
                    </span>
                  </div>
                </div>

                <div class="assignment-side">
                  <div class="deadline-label">
                    Дедлайн
                  </div>

                  <div class="deadline-date">
                    {{ formatDate(item.deadline) }}
                  </div>
                </div>

                <ArrowRight :size="16" class="arrow-icon" />
              </div>
            </div>

            <div v-else class="empty-state">
              Активных заданий нет
            </div>
          </div>

          <!-- RECENT GRADES -->
          <div class="dashboard-card primary-card">
            <div class="card-header">
              <div>
                <h2>Последние оценки</h2>
                <p>Недавно проверенные задания</p>
              </div>
            </div>

            <div
              v-if="dashboardData.recent_grades.length"
              class="grades-list"
            >
              <div
                v-for="item in dashboardData.recent_grades"
                :key="item.id"
                class="grade-item"
              >
                <div class="grade-main">
                  <div class="grade-title">
                    {{ item.assignment_title }}
                  </div>

                  <div class="grade-date">
                    {{ formatDate(item.submitted_at) }}
                  </div>

                  <div
                    v-if="item.tutor_comment"
                    class="tutor-comment"
                  >
                    {{ item.tutor_comment }}
                  </div>
                </div>

                <div class="grade-side">
                  <div
                    class="grade-badge"
                    :class="getGradeVariant(item.grade)"
                  >
                    {{ item.grade }}
                  </div>

                  <button
                    class="btn btn-outline btn-sm"
                    @click="goToAssignment(item.id)"
                  >
                    Открыть
                  </button>
                </div>
              </div>
            </div>

            <div v-else class="empty-state">
              Оценок пока нет
            </div>
          </div>
        </div>

        <!-- RIGHT -->
        <div class="right-column">
          <!-- PROGRESS -->
          <div class="dashboard-card secondary-card">
            <div class="card-header">
              <div>
                <h2>Прогресс</h2>
                <p>Ваш общий прогресс обучения</p>
              </div>
            </div>

            <div class="progress-circle-wrapper">
              <div class="progress-circle">
                <div class="progress-inner">
                  {{ dashboardData.stats.progress_percentage }}%
                </div>
              </div>
            </div>

            <div class="progress-info">
              Выполнено
              {{ dashboardData.stats.completed_count }}
              из
              {{ dashboardData.stats.total_assignments }}
              заданий
            </div>

            <div class="progress-bar">
              <div
                class="progress-fill"
                :style="{
                  width:
                    dashboardData.stats.progress_percentage + '%'
                }"
              ></div>
            </div>
          </div>

          <!-- PENDING -->
          <div class="dashboard-card secondary-card">
            <div class="card-header">
              <div>
                <h2>Ожидают проверки</h2>
                <p>Работы на проверке у преподавателя</p>
              </div>
            </div>

            <div
              v-if="dashboardData.pending_grades.length"
              class="pending-list"
            >
              <div
                v-for="item in dashboardData.pending_grades"
                :key="item.id"
                class="pending-item"
              >
                <div class="pending-main">
                  <div class="pending-title">
                    {{ item.assignment_title }}
                  </div>

                  <div class="pending-date">
                    Сдано:
                    {{ formatDate(item.submitted_at) }}
                  </div>
                </div>

                <div class="pending-badge">
                  Проверяется
                </div>
              </div>
            </div>

            <div v-else class="ok-state">
              Все работы проверены
            </div>
          </div>

          <!-- TUTORS -->
          <div class="dashboard-card secondary-card">
            <div class="card-header">
              <div>
                <h2>Мои репетиторы</h2>
                <p>Преподаватели и активность</p>
              </div>
            </div>

            <div
              v-if="dashboardData.my_tutors.length"
              class="tutors-list"
            >
              <div
                v-for="tutor in dashboardData.my_tutors"
                :key="tutor.tutor_id"
                class="tutor-item"
              >
                <div class="tutor-main">
                  <div class="tutor-avatar">
                    <GraduationCap :size="18" />
                  </div>

                  <div>
                    <div class="tutor-name">
                      {{ tutor.tutor_name }}
                    </div>

                    <div class="tutor-meta">
                      Активный преподаватель
                    </div>
                  </div>
                </div>

                <div class="tutor-count">
                  {{ tutor.assignments_count }}
                </div>
              </div>
            </div>

            <div v-else class="empty-state small">
              Репетиторов пока нет
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
  max-width: 700px;
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
}

.hero-subtitle {
  margin-top: 14px;

  font-size: 16px;
  line-height: 1.7;

  color: var(--muted);
}

.hero-btn {
  height: 48px;
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
    box-shadow .2s ease;
}

.stat-card:hover {
  transform: translateY(-3px);

  box-shadow:
    0 14px 40px rgba(15,23,42,0.06);
}

.stat-top {
  margin-bottom: 20px;
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

.stat-icon.success {
  background: rgba(16,185,129,0.10);
  color: var(--success);
}

.stat-icon.warning {
  background: rgba(245,158,11,0.10);
  color: #d97706;
}

.stat-icon.purple {
  background: rgba(139,92,246,0.10);
  color: #7c3aed;
}

.stat-value {
  font-size: 34px;
  line-height: 1;

  font-weight: 800;
  letter-spacing: -0.04em;

  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: var(--muted);
}

/* MAIN GRID */

.main-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.6fr) minmax(320px, 420px);
  gap: 24px;
}

.left-column,
.right-column {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.right-column {
  position: sticky;
  top: 88px;
  align-self: start;
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

/* ASSIGNMENTS */

.assignment-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.assignment-item {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 16px;

  align-items: center;

  padding: 18px;

  border-radius: 18px;
  border: 1px solid transparent;

  cursor: pointer;

  transition: all .18s ease;
}

.assignment-item:hover {
  background: rgba(30,58,138,0.04);

  border-color: rgba(30,58,138,0.05);

  transform: translateX(2px);
}

.assignment-title {
  font-size: 15px;
  font-weight: 700;

  margin-bottom: 8px;
}

.assignment-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;

  font-size: 13px;
  color: var(--muted);
}

.subject-chip {
  padding: 4px 10px;

  border-radius: 999px;

  background: rgba(30,58,138,0.08);

  color: var(--primary);

  font-size: 12px;
  font-weight: 600;
}

.assignment-side {
  text-align: right;
}

.deadline-label {
  font-size: 12px;
  color: var(--muted);

  margin-bottom: 4px;
}

.deadline-date {
  font-size: 13px;
  font-weight: 700;

  color: var(--danger);
}

.arrow-icon {
  color: var(--muted);
}

/* GRADES */

.grades-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.grade-item {
  display: flex;
  justify-content: space-between;
  gap: 18px;

  padding: 18px;

  border-radius: 18px;

  background: #fafafa;
}

.grade-main {
  flex: 1;
}

.grade-title {
  font-size: 15px;
  font-weight: 700;

  margin-bottom: 6px;
}

.grade-date {
  font-size: 13px;
  color: var(--muted);

  margin-bottom: 10px;
}

.tutor-comment {
  font-size: 13px;
  line-height: 1.6;

  color: var(--text);

  padding: 12px;

  background: white;

  border-radius: 12px;
}

.grade-side {
  display: flex;
  flex-direction: column;
  gap: 12px;

  align-items: center;
}

.grade-badge {
  width: 54px;
  height: 54px;

  border-radius: 18px;

  display: flex;
  align-items: center;
  justify-content: center;

  font-size: 20px;
  font-weight: 800;

  color: white;
}

.grade-badge.success {
  background: var(--success);
}

.grade-badge.warning {
  background: var(--reminder);
}

.grade-badge.danger {
  background: var(--danger);
}

/* PROGRESS */

.progress-circle-wrapper {
  display: flex;
  justify-content: center;

  margin: 12px 0 20px;
}

.progress-circle {
  width: 140px;
  height: 140px;

  border-radius: 999px;

  display: flex;
  align-items: center;
  justify-content: center;

  background:
    radial-gradient(
      white 58%,
      transparent 60%
    ),
    conic-gradient(
      var(--primary)
      0%
      calc(var(--progress, 75) * 1%),
      #e5e7eb
      0%
    );
}

.progress-inner {
  font-size: 28px;
  font-weight: 800;
}

.progress-info {
  text-align: center;

  font-size: 14px;
  color: var(--muted);

  margin-bottom: 20px;
}

.progress-bar {
  height: 10px;

  border-radius: 999px;

  overflow: hidden;

  background: #eef2f7;
}

.progress-fill {
  height: 100%;

  border-radius: inherit;

  background:
    linear-gradient(
      90deg,
      var(--primary),
      #3b82f6
    );
}

/* PENDING */

.pending-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.pending-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 14px;

  padding: 14px;

  border-radius: 16px;

  background: rgba(245,158,11,0.08);
}

.pending-title {
  font-size: 14px;
  font-weight: 700;

  margin-bottom: 4px;
}

.pending-date {
  font-size: 13px;
  color: var(--muted);
}

.pending-badge {
  padding: 6px 12px;

  border-radius: 999px;

  background: rgba(245,158,11,0.14);

  color: #b45309;

  font-size: 12px;
  font-weight: 700;
}

/* TUTORS */

.tutors-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.tutor-item {
  display: flex;
  justify-content: space-between;
  align-items: center;

  padding: 14px;

  border-radius: 16px;

  background: white;
}

.tutor-main {
  display: flex;
  align-items: center;
  gap: 12px;
}

.tutor-avatar {
  width: 42px;
  height: 42px;

  border-radius: 14px;

  display: flex;
  align-items: center;
  justify-content: center;

  background: rgba(30,58,138,0.08);

  color: var(--primary);
}

.tutor-name {
  font-size: 14px;
  font-weight: 700;

  margin-bottom: 4px;
}

.tutor-meta {
  font-size: 12px;
  color: var(--muted);
}

.tutor-count {
  min-width: 36px;
  height: 36px;

  border-radius: 12px;

  display: flex;
  align-items: center;
  justify-content: center;

  background: rgba(30,58,138,0.08);

  color: var(--primary);

  font-size: 13px;
  font-weight: 700;
}

/* STATES */

.empty-state {
  padding: 36px 18px;

  text-align: center;

  color: var(--muted);
  font-size: 14px;
}

.empty-state.small {
  padding: 24px 12px;
}

.ok-state {
  padding: 18px;

  border-radius: 16px;

  background: rgba(16,185,129,0.08);

  color: var(--success);

  text-align: center;

  font-size: 14px;
  font-weight: 700;
}

.error-state {
  padding: 24px;

  border-radius: 18px;

  background: rgba(239,68,68,0.08);

  color: var(--danger);
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

  .assignment-item {
    grid-template-columns: 1fr;
  }

  .grade-item {
    flex-direction: column;
  }

  .grade-side {
    flex-direction: row;
    justify-content: space-between;
  }

  .dashboard-card {
    padding: 20px;
  }
}
</style>
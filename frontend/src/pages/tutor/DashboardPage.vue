<script setup lang="ts">
import { ref, onMounted } from 'vue'
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

const isOverdue = (deadline: string) => {
  return new Date(deadline) < new Date()
}

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

const goToAssignment = (id: number) => {
  router.push(`/tutor/assignments/${id}`)
}

const goToStudents = () => {
  router.push('/tutor/students')
}

const createNewAssignment = () => {
  router.push('/tutor/assignments/create')
}
</script>

<template>
  <div class="page">
    <div class="dashboard-header">
      <h1 class="page-title">Дашборд репетитора</h1>
      <p class="muted">Обзор учеников, заданий и прогресса</p>
    </div>

    <div v-if="loading" class="loading">Загрузка...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="dashboardData" class="dashboard-grid">
      
      <!-- Блок 1: Ближайшие дедлайны -->
      <div class="card deadlines-card">
        <div class="card-header">
          <h2 class="card-title">📅 Ближайшие дедлайны</h2>
        </div>
        <div v-if="dashboardData.upcoming_deadlines.length > 0" class="card-content">
          <ul class="deadline-list">
            <li v-for="item in dashboardData.upcoming_deadlines" :key="item.id" class="deadline-item">
              <div class="deadline-info">
                <span class="assignment-name">{{ item.assignment_title }}</span>
                <span class="student-name">{{ item.student_name }}</span>
              </div>
              <div class="deadline-meta">
                <span :class="['deadline-date', { overdue: isOverdue(item.deadline) }]">
                  {{ formatDate(item.deadline) }}
                </span>
                <span :class="['status-badge', item.status]">{{ item.status }}</span>
              </div>
              <button class="btn btn-sm btn-primary" @click="goToAssignment(item.id)">
                Перейти к заданию
              </button>
            </li>
          </ul>
        </div>
        <div v-else class="empty-state">Нет активных назначений</div>
      </div>

      <!-- Блок 2: Статистика по заданиям -->
      <div class="card stats-card">
        <div class="card-header">
          <h2 class="card-title">📊 Статистика по заданиям</h2>
        </div>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-value">{{ dashboardData.assignment_stats.total_assignments }}</div>
            <div class="stat-label">Всего заданий</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ dashboardData.assignment_stats.active_assignments }}</div>
            <div class="stat-label">Активных назначений</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ dashboardData.assignment_stats.submitted_pending }}</div>
            <div class="stat-label">Ожидают проверки</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ dashboardData.assignment_stats.graded_count }}</div>
            <div class="stat-label">Проверено</div>
          </div>
        </div>
      </div>

      <!-- Блок 3: Последние созданные задания -->
      <div class="card recent-card">
        <div class="card-header">
          <h2 class="card-title">📝 Последние задания</h2>
          <button class="btn btn-primary btn-sm" @click="createNewAssignment">
            + Создать новое
          </button>
        </div>
        <div v-if="dashboardData.recent_assignments.length > 0" class="card-content">
          <ul class="recent-list">
            <li v-for="item in dashboardData.recent_assignments" :key="item.id" class="recent-item">
              <div class="recent-info">
                <span class="recent-title">{{ item.title }}</span>
                <span class="recent-subject">{{ item.subject }}</span>
              </div>
              <div class="recent-meta">
                <span class="recent-date">{{ formatDate(item.created_at) }}</span>
                <span class="students-count">{{ item.students_count }} учеников</span>
              </div>
              <button class="btn btn-sm btn-outline" @click="goToAssignment(item.id)">
                Открыть
              </button>
            </li>
          </ul>
        </div>
        <div v-else class="empty-state">Заданий ещё нет</div>
      </div>

      <!-- Блок 4: Активные ученики -->
      <div class="card students-card">
        <div class="card-header">
          <h2 class="card-title">👥 Активные ученики</h2>
          <button class="btn btn-outline btn-sm" @click="goToStudents">
            Все ученики
          </button>
        </div>
        <div v-if="dashboardData.active_students.length > 0" class="card-content">
          <ul class="students-list">
            <li v-for="student in dashboardData.active_students" :key="student.id" class="student-item">
              <div class="student-info">
                <span class="student-name">{{ student.first_name }} {{ student.last_name }}</span>
                <span class="student-email">{{ student.email }}</span>
              </div>
              <div class="student-pending" v-if="student.pending_assignments_count > 0">
                {{ student.pending_assignments_count }} не сдано
              </div>
            </li>
          </ul>
        </div>
        <div v-else class="empty-state">Нет активных учеников</div>
      </div>

      <!-- Блок 5: Требуют внимания -->
      <div class="card attention-card">
        <div class="card-header">
          <h2 class="card-title">⚠️ Требуют внимания</h2>
        </div>
        <div class="attention-sections">
          <!-- Сдано, но не оценено -->
          <div class="attention-section">
            <h3 class="attention-subtitle">
              Ожидают оценки ({{ dashboardData.needs_attention.submitted_pending_count }})
            </h3>
            <ul v-if="dashboardData.needs_attention.submitted_pending.length > 0" class="attention-list">
              <li v-for="item in dashboardData.needs_attention.submitted_pending" :key="item.id" class="attention-item">
                <span class="attention-title">{{ item.assignment_title }}</span>
                <span class="attention-student">{{ item.student_name }}</span>
                <button class="btn btn-sm btn-primary" @click="goToAssignment(item.id)">
                  Проверить
                </button>
              </li>
            </ul>
            <div v-else class="empty-state-mini">Все работы проверены</div>
          </div>

          <!-- Просроченные -->
          <div class="attention-section">
            <h3 class="attention-subtitle overdue-title">
              Просроченные ({{ dashboardData.needs_attention.overdue_count }})
            </h3>
            <ul v-if="dashboardData.needs_attention.overdue.length > 0" class="attention-list">
              <li v-for="item in dashboardData.needs_attention.overdue" :key="item.id" class="attention-item overdue">
                <span class="attention-title">{{ item.assignment_title }}</span>
                <span class="attention-student">{{ item.student_name }}</span>
                <span class="overdue-date">{{ formatDate(item.deadline) }}</span>
                <button class="btn btn-sm btn-danger" @click="goToAssignment(item.id)">
                  Открыть
                </button>
              </li>
            </ul>
            <div v-else class="empty-state-mini">Просрочек нет</div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.dashboard-header {
  margin-bottom: 24px;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 20px;
}

.card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
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
}

.card-content {
  margin-top: 12px;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.stat-item {
  text-align: center;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #2c3e50;
}

.stat-label {
  font-size: 12px;
  color: #7f8c8d;
  margin-top: 4px;
}

/* Lists */
.deadline-list,
.recent-list,
.students-list,
.attention-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.deadline-item,
.recent-item,
.student-item,
.attention-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px 0;
  border-bottom: 1px solid #eee;
}

.deadline-item:last-child,
.recent-item:last-child,
.student-item:last-child,
.attention-item:last-child {
  border-bottom: none;
}

.deadline-info,
.recent-info,
.student-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.assignment-name,
.recent-title,
.student-name,
.attention-title {
  font-weight: 500;
  color: #2c3e50;
}

.student-name,
.recent-subject,
.student-email,
.attention-student {
  font-size: 13px;
  color: #7f8c8d;
}

.deadline-meta,
.recent-meta {
  display: flex;
  gap: 12px;
  align-items: center;
}

.deadline-date {
  font-size: 13px;
  color: #7f8c8d;
}

.deadline-date.overdue {
  color: #e74c3c;
  font-weight: 500;
}

.status-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 12px;
  background: #ecf0f1;
  color: #7f8c8d;
}

.status-badge.assigned {
  background: #3498db;
  color: white;
}

.status-badge.submitted {
  background: #f39c12;
  color: white;
}

.status-badge.graded {
  background: #27ae60;
  color: white;
}

.students-count,
.recent-date {
  font-size: 12px;
  color: #95a5a6;
}

.student-pending {
  font-size: 12px;
  color: #e74c3c;
  font-weight: 500;
}

/* Attention Section */
.attention-sections {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.attention-section {
  padding-bottom: 16px;
  border-bottom: 1px solid #eee;
}

.attention-section:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.attention-subtitle {
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 12px 0;
}

.overdue-title {
  color: #e74c3c;
}

.attention-item {
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
}

.attention-item.overdue {
  background: #fef5f5;
  padding: 8px 12px;
  border-radius: 6px;
  margin-bottom: 8px;
}

.overdue-date {
  font-size: 12px;
  color: #e74c3c;
}

.empty-state {
  text-align: center;
  color: #95a5a6;
  padding: 20px;
}

.empty-state-mini {
  font-size: 13px;
  color: #95a5a6;
  padding: 8px 0;
}

.loading,
.error {
  text-align: center;
  padding: 40px;
  font-size: 16px;
}

.error {
  color: #e74c3c;
}

/* Buttons */
.btn {
  padding: 8px 16px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.btn-sm {
  padding: 4px 12px;
  font-size: 12px;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover {
  background: #2980b9;
}

.btn-outline {
  background: transparent;
  border: 1px solid #3498db;
  color: #3498db;
}

.btn-outline:hover {
  background: #3498db;
  color: white;
}

.btn-danger {
  background: #e74c3c;
  color: white;
}

.btn-danger:hover {
  background: #c0392b;
}

/* Responsive */
@media (max-width: 768px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>


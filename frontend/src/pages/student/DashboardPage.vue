<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
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
    month: 'long',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getGradeColor = (grade: number, maxGrade: number = 10) => {
  const percentage = (grade / maxGrade) * 100
  if (percentage >= 80) return '#27ae60'
  if (percentage >= 60) return '#f39c12'
  return '#e74c3c'
}

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
  router.push(`/student/assignments/${id}`)
}

const goToAssignments = () => {
  router.push('/student/assignments')
}
</script>

<template>
  <div class="page">
    <div class="dashboard-header">
      <h1 class="page-title">Дашборд ученика</h1>
      <p class="muted">Ваши задания, оценки и прогресс</p>
    </div>

    <div v-if="loading" class="loading">Загрузка...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="dashboardData" class="dashboard-grid">
      
      <!-- Блок 1: Активные задания -->
      <div class="card active-card">
        <div class="card-header">
          <h2 class="card-title">📚 Активные задания</h2>
          <button class="btn btn-outline btn-sm" @click="goToAssignments">
            Все задания
          </button>
        </div>
        <div v-if="dashboardData.active_assignments.length > 0" class="card-content">
          <ul class="assignment-list">
            <li v-for="item in dashboardData.active_assignments" :key="item.id" class="assignment-item">
              <div class="assignment-info">
                <span class="assignment-title">{{ item.assignment_title }}</span>
                <span class="assignment-tutor">{{ item.tutor_name }}</span>
                <span class="assignment-subject" v-if="item.subject">{{ item.subject }}</span>
              </div>
              <div class="assignment-meta">
                <span class="deadline-date">Дедлайн: {{ formatDate(item.deadline) }}</span>
              </div>
              <button class="btn btn-sm btn-primary" @click="goToAssignment(item.id)">
                Перейти к заданию
              </button>
            </li>
          </ul>
        </div>
        <div v-else class="empty-state">Нет активных заданий</div>
      </div>

      <!-- Блок 2: Ожидают оценки -->
      <div class="card pending-card">
        <div class="card-header">
          <h2 class="card-title">⏳ Ожидают оценки</h2>
        </div>
        <div v-if="dashboardData.pending_grades.length > 0" class="card-content">
          <ul class="pending-list">
            <li v-for="item in dashboardData.pending_grades" :key="item.id" class="pending-item">
              <div class="pending-info">
                <span class="pending-title">{{ item.assignment_title }}</span>
                <span class="pending-date">Сдано: {{ formatDate(item.submitted_at) }}</span>
              </div>
              <div class="pending-status">
                <span class="status-badge pending">Ожидает проверки</span>
              </div>
            </li>
          </ul>
        </div>
        <div v-else class="empty-state">Все работы проверены</div>
      </div>

      <!-- Блок 3: Последние оценки -->
      <div class="card grades-card">
        <div class="card-header">
          <h2 class="card-title">🎯 Последние оценки</h2>
        </div>
        <div v-if="dashboardData.recent_grades.length > 0" class="card-content">
          <ul class="grades-list">
            <li v-for="item in dashboardData.recent_grades" :key="item.id" class="grades-item">
              <div class="grades-info">
                <span class="grades-title">{{ item.assignment_title }}</span>
                <span class="grades-date">{{ formatDate(item.submitted_at) }}</span>
              </div>
              <div class="grades-result">
                <span 
                  class="grade-badge" 
                  :style="{ backgroundColor: getGradeColor(item.grade) }"
                >
                  {{ item.grade }}
                </span>
                <span v-if="item.tutor_comment" class="tutor-comment" :title="item.tutor_comment">
                  💬 {{ item.tutor_comment.substring(0, 30) }}{{ item.tutor_comment.length > 30 ? '...' : '' }}
                </span>
              </div>
              <button class="btn btn-sm btn-outline" @click="goToAssignment(item.id)">
                Открыть
              </button>
            </li>
          </ul>
        </div>
        <div v-else class="empty-state">Оценок пока нет</div>
      </div>

      <!-- Блок 4: Статистика -->
      <div class="card stats-card">
        <div class="card-header">
          <h2 class="card-title">📊 Статистика</h2>
        </div>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-value">{{ dashboardData.stats.total_assignments }}</div>
            <div class="stat-label">Всего заданий</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ dashboardData.stats.completed_count }}</div>
            <div class="stat-label">Выполнено</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ dashboardData.stats.average_grade }}</div>
            <div class="stat-label">Средний балл</div>
          </div>
        </div>
        
        <!-- Прогресс бар -->
        <div class="progress-section">
          <div class="progress-label">
            <span>Прогресс выполнения</span>
            <span>{{ dashboardData.stats.progress_percentage }}%</span>
          </div>
          <div class="progress-bar">
            <div 
              class="progress-fill" 
              :style="{ width: dashboardData.stats.progress_percentage + '%' }"
            ></div>
          </div>
        </div>
      </div>

      <!-- Блок 5: Мои репетиторы -->
      <div class="card tutors-card">
        <div class="card-header">
          <h2 class="card-title">👨‍🏫 Мои репетиторы</h2>
        </div>
        <div v-if="dashboardData.my_tutors.length > 0" class="card-content">
          <ul class="tutors-list">
            <li v-for="tutor in dashboardData.my_tutors" :key="tutor.tutor_id" class="tutor-item">
              <div class="tutor-info">
                <span class="tutor-name">{{ tutor.tutor_name }}</span>
              </div>
              <div class="tutor-count">
                {{ tutor.assignments_count }} зад.
              </div>
            </li>
          </ul>
        </div>
        <div v-else class="empty-state">Репетиторов пока нет</div>
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
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.stat-item {
  text-align: center;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #2c3e50;
}

.stat-label {
  font-size: 11px;
  color: #7f8c8d;
  margin-top: 4px;
}

/* Progress Bar */
.progress-section {
  margin-top: 20px;
}

.progress-label {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #7f8c8d;
  margin-bottom: 8px;
}

.progress-bar {
  height: 10px;
  background: #ecf0f1;
  border-radius: 5px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3498db, #2ecc71);
  transition: width 0.3s ease;
}

/* Lists */
.assignment-list,
.pending-list,
.grades-list,
.tutors-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.assignment-item,
.pending-item,
.grades-item,
.tutor-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px 0;
  border-bottom: 1px solid #eee;
}

.assignment-item:last-child,
.pending-item:last-child,
.grades-item:last-child,
.tutor-item:last-child {
  border-bottom: none;
}

.assignment-info,
.pending-info,
.grades-info,
.tutor-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.assignment-title,
.pending-title,
.grades-title,
.tutor-name {
  font-weight: 500;
  color: #2c3e50;
}

.assignment-tutor,
.assignment-subject,
.pending-date,
.grades-date {
  font-size: 13px;
  color: #7f8c8d;
}

.assignment-meta {
  display: flex;
  gap: 12px;
  align-items: center;
}

.deadline-date {
  font-size: 13px;
  color: #e74c3c;
  font-weight: 500;
}

/* Pending Status */
.pending-status {
  display: flex;
  justify-content: flex-end;
}

.status-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 12px;
  background: #ecf0f1;
  color: #7f8c8d;
}

.status-badge.pending {
  background: #f39c12;
  color: white;
}

/* Grades Result */
.grades-result {
  display: flex;
  align-items: center;
  gap: 12px;
}

.grade-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 36px;
  height: 36px;
  border-radius: 50%;
  color: white;
  font-weight: 700;
  font-size: 16px;
}

.tutor-comment {
  font-size: 12px;
  color: #7f8c8d;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Tutor Count */
.tutor-count {
  font-size: 13px;
  color: #7f8c8d;
  background: #f8f9fa;
  padding: 4px 12px;
  border-radius: 12px;
  align-self: flex-start;
}

.empty-state {
  text-align: center;
  color: #95a5a6;
  padding: 20px;
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

/* Responsive */
@media (max-width: 768px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>

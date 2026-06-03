<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getTutorAnalytics } from '@/api/analytics'
import type { TutorAnalyticsData } from '@/api/analytics'
import { Bar as BarChart, Doughnut as DoughnutChart } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const analyticsData = ref<TutorAnalyticsData | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

// Общий средний балл (вычисляется по students_summary)
const overallAverageGrade = computed(() => {
  const students = analyticsData.value?.students_summary
  if (!students || students.length === 0) return null
  const grades = students
    .map(s => s.average_grade)
    .filter((g): g is number => g !== null)
  if (grades.length === 0) return null
  return (grades.reduce((sum, g) => sum + g, 0) / grades.length).toFixed(1)
})

// Данные для столбчатой диаграммы (ученики и их средний балл)
const barChartData = ref<{
  labels: string[]
  datasets: [
    {
      label: string
      backgroundColor: string
      borderColor: string
      borderWidth: number
      borderRadius: number
      data: number[]
    }
  ]
}>({
  labels: [],
  datasets: [
    {
      label: 'Средний балл',
      backgroundColor: 'rgba(30, 58, 138, 0.7)',
      borderColor: 'rgba(30, 58, 138, 1)',
      borderWidth: 1,
      borderRadius: 6,
      data: []
    }
  ]
})

// Опции для столбчатой диаграммы
const barChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    title: { display: true, text: 'Средний балл учеников' }
  },
  scales: {
    y: {
      beginAtZero: true,
      max: 10,
      title: { display: true, text: 'Балл' },
      grid: { color: 'rgba(0, 0, 0, 0.06)' }
    },
    x: {
      grid: { display: false },
      ticks: { maxRotation: 45, minRotation: 0 }
    }
  }
}

// Данные для круговой диаграммы (выполнение заданий)
const doughnutChartData = ref<{
  labels: string[]
  datasets: [
    {
      data: number[]
      backgroundColor: string[]
      borderColor: string[]
      borderWidth: number
    }
  ]
}>({
  labels: ['Назначено', 'Сдано', 'Проверено'],
  datasets: [
    {
      data: [0, 0, 0],
      backgroundColor: [
        'rgba(107, 114, 128, 0.7)',
        'rgba(245, 158, 11, 0.7)',
        'rgba(16, 185, 129, 0.7)'
      ],
      borderColor: [
        'rgba(107, 114, 128, 1)',
        'rgba(245, 158, 11, 1)',
        'rgba(16, 185, 129, 1)'
      ],
      borderWidth: 1
    }
  ]
})

// Опции для круговой диаграммы
const doughnutChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'bottom' as const },
    title: { display: true, text: 'Выполнение заданий' }
  }
}

// Статусы прогресса
const progressStatusMap: Record<string, string> = {
  growing: 'В росте',
  falling: 'Падает',
  stable: 'Стабильный',
  no_change: 'Без изменений'
}

const progressStatusClass: Record<string, string> = {
  growing: 'chip-success',
  falling: 'chip-danger',
  stable: 'chip-warning',
  no_change: ''
}

onMounted(async () => {
  try {
    const data = await getTutorAnalytics()
    analyticsData.value = data

    // Заполняем столбчатую диаграмму учениками, у которых есть средний балл
    const students = data?.students_summary?.filter(s => s.average_grade !== null) ?? []
    if (students.length > 0) {
      barChartData.value.labels = students.map(s => `${s.last_name} ${s.first_name.charAt(0)}.`)
      barChartData.value.datasets[0].data = students.map(s => s.average_grade as number)
    }

    // Заполняем круговую диаграмму
    const completion = data?.assignment_completion
    if (completion) {
      doughnutChartData.value.datasets[0].data = [
        completion.assigned ?? 0,
        completion.submitted ?? 0,
        completion.graded ?? 0
      ]
    }
  } catch (e) {
    error.value = 'Ошибка при загрузке данных аналитики'
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="analytics-page">
    <!-- Заголовок -->
    <header class="page-header">
      <div>
        <h1 class="page-title">Аналитика</h1>
        <p class="page-subtitle">
          Прогресс учеников: средний балл, процент выполненных работ, динамика по заданиям.
        </p>
      </div>
    </header>

    <!-- Состояния загрузки / ошибки -->
    <div v-if="loading" class="card card-center">
      <p class="muted">Загрузка данных...</p>
    </div>
    <div v-else-if="error" class="card card-center">
      <span class="chip chip-danger">{{ error }}</span>
    </div>

    <template v-if="analyticsData">
      <!-- KPI-виджеты -->
      <div class="kpi-grid">
        <div class="kpi-card">
          <span class="kpi-label">Средний балл</span>
          <span class="kpi-value">{{ overallAverageGrade ?? '—' }}</span>
        </div>
        <div class="kpi-card">
          <span class="kpi-label">Выполнено заданий</span>
          <span class="kpi-value">{{ analyticsData.assignment_completion?.total ?? 0 }}</span>
        </div>
        <div class="kpi-card">
          <span class="kpi-label">Учеников</span>
          <span class="kpi-value">{{ analyticsData.students_summary?.length ?? 0 }}</span>
        </div>
      </div>

      <!-- Графики: гистограмма и круговая диаграмма -->
      <div class="charts-grid">
        <!-- Гистограмма среднего балла учеников -->
        <div class="card chart-card">
          <h3 class="card-title">Средний балл учеников</h3>
          <div class="chart-container">
            <BarChart
              v-if="barChartData.labels.length"
              :data="barChartData"
              :options="barChartOptions"
            />
            <div v-else class="empty-chart muted">Нет данных для отображения</div>
          </div>
        </div>

        <!-- Круговая диаграмма выполнения заданий -->
        <div class="card chart-card">
          <h3 class="card-title">Выполнение заданий</h3>
          <div class="chart-container">
            <DoughnutChart
              v-if="analyticsData.assignment_completion && analyticsData.assignment_completion.total > 0"
              :data="doughnutChartData"
              :options="doughnutChartOptions"
            />
            <div v-else class="empty-chart muted">Нет данных для отображения</div>
          </div>
        </div>
      </div>

      <!-- Таблица учеников -->
      <div class="card table-card">
        <h3 class="card-title">Сводка по ученикам</h3>
        <div class="table-responsive">
          <table class="table modern-table">
            <thead>
              <tr>
                <th>Ученик</th>
                <th>Средний балл</th>
                <th>Выполнено</th>
                <th>Прогресс</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="student in analyticsData.students_summary" :key="student.id">
                <td>
                  <div class="student-cell">
                    <div class="avatar">{{ student.first_name.charAt(0) }}{{ student.last_name.charAt(0) }}</div>
                    <span>{{ student.last_name }} {{ student.first_name.charAt(0) }}.</span>
                  </div>
                </td>
                <td>
                  <span v-if="student.average_grade !== null"
                    :class="['chip', student.average_grade >= 7 ? 'chip-success' : student.average_grade >= 5 ? 'chip-warning' : 'chip-danger']">
                    {{ student.average_grade }}
                  </span>
                  <span v-else class="muted">—</span>
                </td>
                <td>
                  <div class="progress-cell">
                    <div class="progress-bar">
                      <div class="progress-fill" :style="{ width: student.completion_percentage + '%' }"
                        :class="{
                          'fill-success': student.completion_percentage >= 80,
                          'fill-warning': student.completion_percentage >= 50 && student.completion_percentage < 80,
                          'fill-danger': student.completion_percentage < 50
                        }"></div>
                    </div>
                    <span class="progress-text">{{ student.completion_percentage }}%</span>
                  </div>
                </td>
                <td>
                  <span :class="['chip', progressStatusClass[student.progress_status] ?? '']">
                    {{ progressStatusMap[student.progress_status] ?? student.progress_status }}
                  </span>
                </td>
              </tr>
              <tr v-if="!analyticsData.students_summary?.length">
                <td colspan="4" class="muted text-center">Нет учеников</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
/* Переменные для современного оформления */
.analytics-page {
  --card-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
  --card-hover-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  --radius: 16px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--primary);
  margin: 0;
}

.page-subtitle {
  margin: 6px 0 0;
  color: var(--muted);
  font-size: 15px;
  line-height: 1.4;
}

.card {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px;
  box-shadow: var(--card-shadow);
  transition: box-shadow 0.2s ease, transform 0.2s ease;
}
.card:hover {
  box-shadow: var(--card-hover-shadow);
}
.card-center {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 120px;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}
.kpi-card {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px 16px;
  box-shadow: var(--card-shadow);
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.kpi-label {
  font-size: 14px;
  color: var(--muted);
  font-weight: 500;
}
.kpi-value {
  font-size: 32px;
  font-weight: 700;
  color: var(--text);
  line-height: 1.2;
}

.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.chart-card {
  display: flex;
  flex-direction: column;
}
.chart-container {
  height: 300px; /* немного выше для столбцов */
  position: relative;
}
.empty-chart {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.table-card {
  overflow: visible;
}
.table-responsive {
  overflow-x: auto;
}
.modern-table {
  width: 100%;
  border-collapse: collapse;
}
.modern-table th {
  text-align: left;
  padding: 10px 12px;
  font-size: 13px;
  font-weight: 600;
  color: var(--muted);
  border-bottom: 1px solid var(--border);
}
.modern-table td {
  padding: 14px 12px;
  border-bottom: 1px solid var(--border);
  font-size: 14px;
  vertical-align: middle;
}
.student-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}
.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--primary);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  flex-shrink: 0;
}

.progress-cell {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 140px;
}
.progress-bar {
  flex: 1;
  height: 8px;
  background: var(--border);
  border-radius: 4px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.4s ease;
  background: var(--muted);
}
.fill-success { background: var(--success); }
.fill-warning { background: var(--reminder); }
.fill-danger { background: var(--danger); }
.progress-text {
  font-weight: 600;
  font-size: 13px;
  min-width: 36px;
  text-align: right;
}

@media (max-width: 900px) {
  .kpi-grid {
    grid-template-columns: 1fr;
  }
  .charts-grid {
    grid-template-columns: 1fr;
  }
}

.text-center { text-align: center; }


@media (max-width: 640px) {
  .kpi-card {
    padding: 12px;
  }
  .kpi-value {
    font-size: 24px;
  }
  .chart-container {
    height: 220px;
  }
  .modern-table th,
  .modern-table td {
    padding: 8px 6px;
    font-size: 13px;
  }
  .student-cell .avatar {
    width: 28px;
    height: 28px;
    font-size: 11px;
  }
  .progress-cell {
    min-width: 100px;
  }
}
</style>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getTutorAnalytics } from '@/api/analytics'
import type { TutorAnalyticsData, StudentSummaryItem } from '@/api/analytics'
import { LineChart, DoughnutChart } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
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

// Опции для линейного графика (средний балл)
const lineChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,
      position: 'top' as const
    },
    title: {
      display: true,
      text: 'Динамика среднего балла'
    }
  },
  scales: {
    y: {
      beginAtZero: false,
      min: 0,
      max: 10,
      title: {
        display: true,
        text: 'Балл'
      }
    }
  }
}

// Данные для линейного графика
const lineChartData = ref({
  labels: [] as string[],
  datasets: [
    {
      label: 'Средний балл',
      backgroundColor: 'rgba(30, 58, 138, 0.2)',
      borderColor: 'rgba(30, 58, 138, 1)',
      data: [] as number[],
      fill: true,
      tension: 0.4
    }
  ]
})

// Опции для круговой диаграммы (выполнение заданий)
const doughnutChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom' as const
    },
    title: {
      display: true,
      text: 'Выполнение заданий'
    }
  }
}

// Данные для круговой диаграммы
const doughnutChartData = ref({
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

// Функция для получения статуса прогресса в русском виде
function getProgressStatusLabel(status: string): string {
  const statusMap: Record<string, string> = {
    'growing': 'В росте',
    'falling': 'Падает',
    'stable': 'Стабильный',
    'no_change': 'Без изменений'
  }
  return statusMap[status] || status
}

// Функция для получения класса чипа в зависимости от статуса
function getProgressChipClass(status: string): string {
  switch (status) {
    case 'growing':
      return 'chip-success'
    case 'falling':
      return 'chip-danger'
    case 'stable':
      return 'chip-warning'
    default:
      return ''
  }
}

onMounted(async () => {
  try {
    const data = await getTutorAnalytics()
    analyticsData.value = data
    
    // Заполняем данные для линейного графика
    if (data.average_grades_chart.length > 0) {
      lineChartData.value.labels = data.average_grades_chart.map(item => item.month)
      lineChartData.value.datasets[0].data = data.average_grades_chart.map(item => item.avg_grade)
    }
    
    // Заполняем данные для круговой диаграммы
    doughnutChartData.value.datasets[0].data = [
      data.assignment_completion.assigned,
      data.assignment_completion.submitted,
      data.assignment_completion.graded
    ]
  } catch (e) {
    error.value = 'Ошибка при загрузке данных аналитики'
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="page">
    <div>
      <h1 class="page-title">Аналитика</h1>
      <p class="muted" style="margin: 8px 0 0 0;">
        Прогресс учеников: средний балл, процент выполненных работ, динамика по заданиям.
      </p>
    </div>

    <div v-if="loading" class="card">
      <p class="muted">Загрузка данных...</p>
    </div>

    <div v-else-if="error" class="card">
      <p class="chip chip-danger">{{ error }}</p>
    </div>

    <template v-else>
      <div class="grid grid-cols-2">
        <!-- График среднего балла -->
        <div class="card">
          <div class="card-title">Средний балл по месяцам</div>
          <div style="height: 250px;">
            <LineChart
              v-if="analyticsData?.average_grades_chart.length"
              :data="lineChartData"
              :options="lineChartOptions"
            />
            <div v-else class="muted" style="display: flex; align-items: center; justify-content: center; height: 100%;">
              Нет данных для отображения
            </div>
          </div>
        </div>

        <!-- Диаграмма выполнения заданий -->
        <div class="card">
          <div class="card-title">Выполнение заданий</div>
          <div style="height: 250px;">
            <DoughnutChart
              v-if="analyticsData?.assignment_completion.total > 0"
              :data="doughnutChartData"
              :options="doughnutChartOptions"
            />
            <div v-else class="muted" style="display: flex; align-items: center; justify-content: center; height: 100%;">
              Нет данных для отображения
            </div>
          </div>
        </div>
      </div>

      <!-- Сводка по ученикам -->
      <div class="card">
        <div class="card-title">Сводка по ученикам</div>
        <div style="overflow-x: auto;">
          <table class="table">
            <thead>
              <tr>
                <th>Ученик</th>
                <th>Средний балл</th>
                <th>Выполнено</th>
                <th>Прогресс</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="student in analyticsData?.students_summary" :key="student.id">
                <td>{{ student.last_name }} {{ student.first_name.charAt(0) }}.</td>
                <td>
                  <span v-if="student.average_grade !== null" :class="['chip', student.average_grade >= 7 ? 'chip-success' : student.average_grade >= 5 ? 'chip-warning' : 'chip-danger']">
                    {{ student.average_grade }}
                  </span>
                  <span v-else class="muted">—</span>
                </td>
                <td>
                  <span :class="['chip', student.completion_percentage >= 80 ? 'chip-success' : student.completion_percentage >= 50 ? 'chip-warning' : 'chip-danger']">
                    {{ student.completion_percentage }}%
                  </span>
                </td>
                <td>
                  <span :class="['chip', getProgressChipClass(student.progress_status)]">
                    {{ getProgressStatusLabel(student.progress_status) }}
                  </span>
                </td>
              </tr>
              <tr v-if="!analyticsData?.students_summary.length">
                <td colspan="4" class="muted" style="text-align: center;">Нет учеников</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>


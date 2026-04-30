<!-- src/pages/student/AssignmentsPage.vue -->
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getStudentAssignments } from '@/api/assignments'
import type { StudentAssignmentListItem } from '@/types/assignments'
import { toApiError } from '@/api/http'

const router = useRouter()
const items = ref<StudentAssignmentListItem[]>([])
const loading = ref(false)
const errorMsg = ref('')

const fetch = async () => {
  loading.value = true
  try {
    items.value = await getStudentAssignments()
  } catch (e) {
    errorMsg.value = toApiError(e).message
  } finally {
    loading.value = false
  }
}

const statusChip = (status: string) => {
  switch (status) {
    case 'graded': return 'chip-success'
    case 'submitted': return 'chip-warning'
    default: return ''
  }
}

const goToDetail = (id: number) => router.push(`/app/student/assignments/${id}`)

onMounted(fetch)
</script>

<template>
  <div class="page">
    <h1 class="page-title">Мои задания</h1>
    <p class="muted">Задания от репетиторов</p>

    <div v-if="loading" class="muted">Загрузка...</div>
    <div v-else-if="errorMsg" class="chip chip-danger">{{ errorMsg }}</div>
    <div v-else-if="items.length === 0" class="card muted">Активных заданий нет</div>

    <div v-else class="card">
      <table class="table">
        <thead>
          <tr><th>Задание</th><th>Дедлайн</th><th>Статус</th></tr>
        </thead>
        <tbody>
          <tr v-for="sa in items" :key="sa.id" @click="goToDetail(sa.id)" style="cursor:pointer;">
            <td>{{ sa.assignment_title }}</td>
            <td>{{ new Date(sa.deadline).toLocaleString() }}</td>
            <td><span class="chip" :class="statusChip(sa.status)">{{ sa.status }}</span></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
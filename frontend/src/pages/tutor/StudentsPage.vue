<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useStudentsStore } from '../../stores/students'
import type { TutorStudentRelation } from '../../types/domain'

const students = useStudentsStore()

const email = ref('')
const subject = ref('')
const localError = ref('')

onMounted(async () => {
  await students.loadTutorStudents()
})

const relations = computed(() => students.relations)
const activeRelations = computed(() => relations.value.filter((r) => r.status === 'active'))
const pendingRelations = computed(() => relations.value.filter((r) => r.status === 'pending'))

async function submitInvite() {
  localError.value = ''
  if (!email.value.trim()) return
  try {
    await students.sendInvitation(email.value.trim(), subject.value.trim())
    email.value = ''
    subject.value = ''
  } catch {
    localError.value = students.error || 'Не удалось отправить приглашение.'
  }
}

function fullName(relation: TutorStudentRelation) {
  return `${relation.student.first_name} ${relation.student.last_name}`.trim() || relation.student.email
}
</script>

<template>
  <div class="page">
    <div>
      <h1 class="page-title">Ученики</h1>
      <p class="muted" style="margin: 8px 0 0 0;">
        Приглашайте учеников по e-mail и управляйте связями.
      </p>
    </div>

    <div class="card">
      <div class="card-title">Отправить приглашение</div>
      <div class="grid grid-cols-2" style="margin-top: 12px;">
        <div>
          <div class="label">E-mail ученика</div>
          <input v-model="email" class="input" type="email" placeholder="student@example.com" />
        </div>
        <div>
          <div class="label">Предмет (необязательно)</div>
          <input v-model="subject" class="input" type="text" placeholder="Алгебра" />
        </div>
      </div>
      <div class="row" style="margin-top: 12px;">
        <button class="btn btn-primary" type="button" @click="submitInvite" :disabled="students.loading || !email.trim()">
          Отправить инвайт
        </button>
        <span v-if="localError || students.error" style="color: #ef4444;">
          {{ localError || students.error }}
        </span>
      </div>
    </div>

    <div class="card">
      <div class="card-title">Активные ученики</div>
      <div style="overflow-x: auto; margin-top: 12px;">
        <table class="table">
          <thead>
            <tr>
              <th>Имя</th>
              <th>Email</th>
              <th>Предмет</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in activeRelations" :key="r.id">
              <td>{{ fullName(r) }}</td>
              <td>{{ r.student.email }}</td>
              <td>{{ r.subject || '—' }}</td>
            </tr>
            <tr v-if="activeRelations.length === 0">
              <td colspan="3" class="muted">Пока нет активных учеников</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="card">
      <div class="card-title">Ожидают подтверждения</div>
      <div style="overflow-x: auto; margin-top: 12px;">
        <table class="table">
          <thead>
            <tr>
              <th>Имя</th>
              <th>Email</th>
              <th>Предмет</th>
              <th>Статус</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in pendingRelations" :key="r.id">
              <td>{{ fullName(r) }}</td>
              <td>{{ r.student.email }}</td>
              <td>{{ r.subject || '—' }}</td>
              <td>{{ r.status }}</td>
            </tr>
            <tr v-if="pendingRelations.length === 0">
              <td colspan="4" class="muted">Нет ожидающих приглашений</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useStudentsStore } from '../../stores/students'

const students = useStudentsStore()

onMounted(() => {
  void students.loadStudentPendingInvitations()
})

async function accept(id: number) {
  await students.processInvitation(id, 'accept')
}

async function reject(id: number) {
  await students.processInvitation(id, 'cancel')
}
</script>

<template>
  <div class="page">
    <div>
      <h1 class="page-title">Приглашения</h1>
      <p class="muted" style="margin: 8px 0 0 0;">Примите или отмените приглашение от репетитора.</p>
    </div>

    <div class="card">
      <div v-if="students.error" style="color: #ef4444; margin-bottom: 12px;">{{ students.error }}</div>
      <table class="table">
        <thead>
          <tr>
            <th>Репетитор</th>
            <th>Email</th>
            <th>Предмет</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="invite in students.pendingInvitations" :key="invite.id">
            <td>{{ `${invite.tutor.first_name} ${invite.tutor.last_name}`.trim() || invite.tutor.email }}</td>
            <td>{{ invite.tutor.email }}</td>
            <td>{{ invite.subject || '—' }}</td>
            <td>
              <div class="row">
                <button class="btn btn-primary" type="button" @click="accept(invite.id)">Принять</button>
                <button class="btn" type="button" @click="reject(invite.id)">Отменить</button>
              </div>
            </td>
          </tr>
          <tr v-if="students.pendingInvitations.length === 0">
            <td colspan="4" class="muted">Новых приглашений нет</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

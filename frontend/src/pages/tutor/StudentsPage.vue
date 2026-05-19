<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useStudentsStore } from '../../stores/students'
import type { TutorStudentRelation } from '../../types/domain'
import BaseModal from '@/components/ui/BaseModal.vue'

const students = useStudentsStore()

const email = ref('')
const subject = ref('')
const localError = ref('')
const showInviteModal = ref(false)

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
    showInviteModal.value = false
  } catch {
    localError.value = students.error || 'Не удалось отправить приглашение.'
  }
}

function fullName(relation: TutorStudentRelation) {
  return `${relation.student.first_name} ${relation.student.last_name}`.trim() || relation.student.email
}

function openInviteModal() {
  email.value = ''
  subject.value = ''
  localError.value = ''
  showInviteModal.value = true
}
</script>

<template>
  <div class="page">
    <div class="row" style="justify-content: space-between; align-items: flex-start;">
      <div>
        <h1 class="page-title">Ученики</h1>
        <p class="muted" style="margin: 8px 0 0 0;">
          Приглашайте учеников по e-mail и управляйте связями.
        </p>
      </div>
      <button class="btn btn-primary" @click="openInviteModal">+ Пригласить ученика</button>
    </div>

    <!-- Active Students Card -->
    <div class="card" style="margin-top: 20px;">
      <div class="card-title">Активные ученики ({{ activeRelations.length }})</div>
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

    <!-- Pending Invitations Card -->
    <div class="card" style="margin-top: 20px;">
      <div class="card-title">Ожидают подтверждения ({{ pendingRelations.length }})</div>
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
              <td><span class="chip chip-warning">{{ r.status }}</span></td>
            </tr>
            <tr v-if="pendingRelations.length === 0">
              <td colspan="4" class="muted">Нет ожидающих приглашений</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Invite Student Modal -->
    <BaseModal :show="showInviteModal" @close="showInviteModal = false">
      <div class="modal-header">
        <h2 style="margin: 0;">Пригласить ученика</h2>
        <p class="muted" style="margin: 8px 0 0 0; font-size: 14px;">
          Отправьте приглашение ученику по электронной почте. После регистрации он сможет видеть ваши задания.
        </p>
      </div>
      
      <form class="form" @submit.prevent="submitInvite" style="margin-top: 20px;">
        <div class="form-group">
          <label class="label">E-mail ученика *</label>
          <input 
            v-model="email" 
            class="input" 
            type="email" 
            placeholder="student@example.com" 
            required
            autofocus
          />
        </div>
        
        <div class="form-group">
          <label class="label">Предмет (необязательно)</label>
          <input 
            v-model="subject" 
            class="input" 
            type="text" 
            placeholder="Например, Алгебра" 
          />
          <p class="muted" style="font-size: 13px; margin-top: 4px;">
            Укажите предмет, если хотите привязать ученика к конкретному предмету
          </p>
        </div>
        
        <div v-if="localError || students.error" class="alert alert-error" style="margin-top: 16px;">
          {{ localError || students.error }}
        </div>
        
        <div class="modal-actions" style="margin-top: 24px;">
          <button 
            type="button" 
            class="btn" 
            @click="showInviteModal = false"
          >
            Отмена
          </button>
          <button 
            type="submit" 
            class="btn btn-primary" 
            :disabled="students.loading || !email.trim()"
          >
            {{ students.loading ? 'Отправка...' : 'Отправить приглашение' }}
          </button>
        </div>
      </form>
    </BaseModal>
  </div>
</template>

<style scoped>
.modal-header {
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 16px;
}

.alert {
  padding: 12px 16px;
  border-radius: var(--radius-md);
  font-size: 14px;
}

.alert-error {
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>

import { defineStore } from 'pinia'
import { actOnInvitation, inviteStudent, listPendingInvitations, listTutorStudentRelations } from '../api/invitations'
import type { Student, TutorStudentRelation } from '../types/domain'
import { toApiError } from '../api/http'

export const useStudentsStore = defineStore('students', {
  state: () => ({
    students: [] as Student[],
    relations: [] as TutorStudentRelation[],
    pendingInvitations: [] as TutorStudentRelation[],
    loading: false,
    error: '' as string,
  }),
  getters: {
    getAll: (state) => state.students,
    getById: (state) => (id: string) => state.students.find((s) => s.id === id) ?? null,
    activeRelations: (state) => state.relations.filter((r) => r.status === 'active'),
    activeStudents: (state) =>
      state.relations
        .filter((r) => r.status === 'active')
        .map((r) => ({
          id: String(r.student.id),
          name: `${r.student.first_name} ${r.student.last_name}`.trim() || r.student.email,
          email: r.student.email,
          subject: r.subject ?? '',
        })),
  },
  actions: {
    seedForRole() {
      this.students = []
      this.relations = []
      this.pendingInvitations = []
      this.error = ''
    },

    async loadTutorStudents(status?: string) {
      this.loading = true
      this.error = ''
      try {
        this.relations = await listTutorStudentRelations(status)
        this.students = this.activeStudents
      } catch (err) {
        this.error = toApiError(err).message
      } finally {
        this.loading = false
      }
    },

    async loadStudentPendingInvitations() {
      this.loading = true
      this.error = ''
      try {
        this.pendingInvitations = await listPendingInvitations()
      } catch (err) {
        this.error = toApiError(err).message
      } finally {
        this.loading = false
      }
    },

    async sendInvitation(studentEmail: string, subject?: string) {
      this.error = ''
      try {
        await inviteStudent(studentEmail, subject)
        await this.loadTutorStudents()
      } catch (err) {
        this.error = toApiError(err).message
        throw err
      }
    },

    async processInvitation(id: number, action: 'accept' | 'reject' | 'cancel') {
      this.error = ''
      try {
        await actOnInvitation(id, action)
        await this.loadStudentPendingInvitations()
      } catch (err) {
        this.error = toApiError(err).message
        throw err
      }
    },
  },
})


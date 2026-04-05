import { defineStore } from 'pinia'
import type { Role } from '../types/roles'
import type { Student, StudentGroupType } from '../types/domain'

const demoStudents: Student[] = [
  {
    id: 's-anna',
    name: 'Анна',
    email: 'anna@example.com',
    subject: 'Алгебра',
    groupType: 'private',
  },
  {
    id: 's-ilya',
    name: 'Илья',
    email: 'ilya@example.com',
    subject: 'Русский',
    groupType: 'private',
  },
  {
    id: 's-masha',
    name: 'Маша',
    email: 'masha@example.com',
    subject: 'Английский',
    groupType: 'group',
  },
  {
    id: 's-sergey',
    name: 'Сергей',
    email: 'sergey@example.com',
    subject: 'Геометрия',
    groupType: 'group',
  },
]

export const useStudentsStore = defineStore('students', {
  state: () => ({
    students: [] as Student[],
  }),
  getters: {
    getByGroup: (state) => (group: StudentGroupType) => state.students.filter((s) => s.groupType === group),
    getAll: (state) => state.students,
    getById: (state) => (id: string) => state.students.find((s) => s.id === id) ?? null,
  },
  actions: {
    seedForRole(role: Role) {
      // MVP:
      // - tutor sees all demo students
      // - student sees only their own demo profile(s)
      if (role === 'tutor') {
        this.students = demoStudents
      } else if (role === 'student') {
        this.students = demoStudents.filter((s) => s.id === 's-anna' || s.id === 's-ilya')
      } else {
        this.students = []
      }
    },
    createStudent(payload: Omit<Student, 'id'>) {
      const id = `s-${Math.random().toString(16).slice(2, 8)}`
      this.students.push({ ...payload, id })

      // API (later):
      // await createStudentApi(payload)
    },
    updateStudent(id: string, payload: Omit<Student, 'id'>) {
      const idx = this.students.findIndex((s) => s.id === id)
      if (idx === -1) return
      const existing = this.students[idx]
      if (!existing) return
      this.students[idx] = { ...existing, ...payload, id: existing.id }

      // API (later):
      // await updateStudentApi(id, payload)
    },
    deleteStudent(id: string) {
      this.students = this.students.filter((s) => s.id !== id)

      // API (later):
      // await deleteStudentApi(id)
    },
  },
})


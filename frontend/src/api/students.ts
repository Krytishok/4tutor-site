import { http, toApiError } from './http'
import type { Student, StudentGroupType } from '../types/domain'

// API-контракт для будущей интеграции.
// Сейчас эти функции не вызываются (MVP работает локально).

export async function listStudents(groupType?: StudentGroupType): Promise<Student[]> {
  try {
    const params = groupType ? { groupType } : undefined
    const res = await http.get<Student[]>('/students/', { params })
    return res.data
  } catch (err) {
    const apiErr = toApiError(err)
    throw apiErr
  }
}

export async function createStudent(payload: Omit<Student, 'id'>): Promise<Student> {
  try {
    const res = await http.post<Student>('/students/', payload)
    return res.data
  } catch (err) {
    const apiErr = toApiError(err)
    throw apiErr
  }
}

export async function updateStudent(id: string, payload: Omit<Student, 'id'>): Promise<Student> {
  try {
    const res = await http.patch<Student>(`/students/${id}/`, payload)
    return res.data
  } catch (err) {
    const apiErr = toApiError(err)
    throw apiErr
  }
}

export async function deleteStudent(id: string): Promise<void> {
  try {
    await http.delete(`/students/${id}/`)
  } catch (err) {
    const apiErr = toApiError(err)
    throw apiErr
  }
}


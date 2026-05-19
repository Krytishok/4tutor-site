// src/api/assignments.ts

import { http } from './http'  
import type {
  Assignment,
  AssignmentListItem,
  AssignmentFile,
  StudentAssignment,
  StudentAssignmentListItem,
  SubmissionFile,
  AssignStudentsPayload,
} from '@/types/assignments'

export interface AssignmentFilters {
  search?: string
  subject?: string
  deadline_before?: string
  deadline_after?: string
  status?: string
  page?: number
  page_size?: number
}

export interface PaginatedResponse<T> {
  results: T[]
  pagination: {
    page: number
    page_size: number
    total: number
    total_pages: number
  }
}

function multipartPost<T>(url: string, formData: FormData): Promise<T> {
  return http.post<T>(url, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }).then(res => res.data)
}

// ---------- Задания ----------
export function getAssignments(filters?: AssignmentFilters): Promise<PaginatedResponse<AssignmentListItem>> {
  const params = filters ? { ...filters } : undefined
  return http.get<PaginatedResponse<AssignmentListItem>>('/v1/assignments/', { params }).then(res => res.data)
}

export function getAssignmentDetail(id: number): Promise<Assignment> {
  return http.get<Assignment>(`/v1/assignments/${id}/`).then(res => res.data)
}

export function deleteAssignment(id: number): Promise<void> {
  return http.delete(`/v1/assignments/${id}/`).then(() => undefined)
}

export function createAssignment(payload: {
  title: string
  description?: string
  subject?: string
  files?: File[]
  students?: number[]
  deadline?: string
}): Promise<Assignment> {
  const fd = new FormData()
  fd.append('title', payload.title)
  if (payload.description) fd.append('description', payload.description)
  if (payload.subject) fd.append('subject', payload.subject)
  if (payload.files) payload.files.forEach(f => fd.append('files', f))
  if (payload.students) payload.students.forEach(id => fd.append('students', String(id)))
  if (payload.deadline) fd.append('deadline', payload.deadline)
  return multipartPost<Assignment>('v1/assignments/', fd)
}

export function uploadAssignmentFile(assignmentId: number, file: File): Promise<AssignmentFile> {
  const fd = new FormData()
  fd.append('file', file)
  return http.post<AssignmentFile>(`/v1/assignments/${assignmentId}/upload-file/`, fd, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }).then(res => res.data)
}

export function assignStudentsToAssignment(
  assignmentId: number,
  payload: AssignStudentsPayload,
): Promise<{ assigned: { student_id: number; status: string }[]; errors: any[] }> {
  return http.post(`/v1/assignments/${assignmentId}/assign-students/`, payload).then(res => res.data)
}

// ---------- StudentAssignment ----------
export function getStudentAssignments(filters?: AssignmentFilters): Promise<PaginatedResponse<StudentAssignmentListItem>> {
  const params = filters ? { ...filters } : undefined
  return http.get<PaginatedResponse<StudentAssignmentListItem>>('/v1/assignments/student-assignments/', { params }).then(res => res.data)
}

export function getStudentAssignmentDetail(pk: number): Promise<StudentAssignment> {
  return http.get<StudentAssignment>(`/v1/assignments/student-assignments/${pk}/`).then(res => res.data)
}

export function submitAssignment(pk: number): Promise<{ status: string }> {
  return http.patch(`/v1/assignments/student-assignments/${pk}/`, { submit: true }).then(res => res.data)
}

export function gradeAssignment(pk: number, grade: number, comment: string): Promise<StudentAssignment> {
  return http.patch<StudentAssignment>(`/v1/assignments/student-assignments/${pk}/`, {
    grade,
    tutor_comment: comment,
  }).then(res => res.data)
}

export function uploadSubmissionFile(studentAssignmentId: number, file: File): Promise<SubmissionFile> {
  const fd = new FormData()
  fd.append('file', file)
  return http.post<SubmissionFile>(
    `/v1/assignments/student-assignments/${studentAssignmentId}/upload/`,
    fd,
    { headers: { 'Content-Type': 'multipart/form-data' } },
  ).then(res => res.data)
}

export function updateAssignment(
  id: number,
  payload: {
    title?: string
    description?: string
    subject?: string
    max_grade?: number
    files?: File[]
    remove_file_ids?: number[]
    students?: { student_id: number; deadline: string }[]
  }
): Promise<Assignment> {
  const fd = new FormData()
  if (payload.title !== undefined) fd.append('title', payload.title)
  if (payload.description !== undefined) fd.append('description', payload.description)
  if (payload.subject !== undefined) fd.append('subject', payload.subject)
  if (payload.max_grade !== undefined) fd.append('max_grade', String(payload.max_grade))
  if (payload.files) payload.files.forEach(f => fd.append('files', f))
  if (payload.remove_file_ids) {
    payload.remove_file_ids.forEach(id => fd.append('remove_file_ids', String(id)))
  }
  if (payload.students) {
    // Передаём как JSON-строку
    fd.append('students', JSON.stringify(payload.students))
  }

  return http.patch<Assignment>(`/v1/assignments/${id}/`, fd, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }).then(res => res.data)
}
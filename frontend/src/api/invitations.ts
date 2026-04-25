import { http, toApiError } from './http'
import type { TutorStudentRelation } from '../types/domain'

export async function inviteStudent(studentEmail: string, subject?: string): Promise<TutorStudentRelation> {
  try {
    const res = await http.post<TutorStudentRelation>('/v1/tutor-students/invite/', {
      student_email: studentEmail,
      subject: subject?.trim() || undefined,
    })
    return res.data
  } catch (err) {
    throw toApiError(err)
  }
}

export async function listTutorStudentRelations(status?: string): Promise<TutorStudentRelation[]> {
  try {
    const params = status ? { status } : undefined
    const res = await http.get<TutorStudentRelation[]>('/v1/tutor-students/', { params })
    return res.data
  } catch (err) {
    throw toApiError(err)
  }
}

export async function listPendingInvitations(): Promise<TutorStudentRelation[]> {
  try {
    const res = await http.get<TutorStudentRelation[]>('/v1/tutor-students/pending/')
    return res.data
  } catch (err) {
    throw toApiError(err)
  }
}

export async function actOnInvitation(id: number, action: 'accept' | 'reject' | 'cancel'): Promise<void> {
  try {
    await http.patch(`/v1/tutor-students/${id}/action/`, { action })
  } catch (err) {
    throw toApiError(err)
  }
}

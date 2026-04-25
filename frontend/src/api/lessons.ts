import { http, toApiError } from './http'
import type { Lesson, LessonStatus } from '../types/domain'

type LessonPayload = {
  students: number[]
  subject: string
  start_time: string
  end_time: string
  meeting_url?: string | null
  is_recurring_weekly?: boolean
  status?: LessonStatus
}

export async function listLessons(params?: {
  from?: string
  to?: string
  weekdays_only?: boolean
}): Promise<Lesson[]> {
  try {
    const res = await http.get<Lesson[]>('/v1/lessons/', { params })
    return res.data
  } catch (err) {
    throw toApiError(err)
  }
}

export async function createLesson(payload: LessonPayload): Promise<Lesson> {
  try {
    const res = await http.post<Lesson>('/v1/lessons/', payload)
    return res.data
  } catch (err) {
    throw toApiError(err)
  }
}

export async function updateLesson(id: number, payload: LessonPayload): Promise<Lesson> {
  try {
    const res = await http.patch<Lesson>(`/v1/lessons/${id}/`, payload)
    return res.data
  } catch (err) {
    throw toApiError(err)
  }
}

export async function deleteLesson(id: number): Promise<void> {
  try {
    await http.delete(`/v1/lessons/${id}/`)
  } catch (err) {
    throw toApiError(err)
  }
}

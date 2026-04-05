import { http, toApiError } from './http'
import type { ScheduleEvent } from '../types/domain'

// API-контракт для будущей интеграции расписания.
// Сейчас функции не вызываются (MVP локальный).

export async function listScheduleEvents(fromIso: string, toIso: string): Promise<ScheduleEvent[]> {
  try {
    const res = await http.get<ScheduleEvent[]>('/schedule/events/', {
      params: { from: fromIso, to: toIso },
    })
    return res.data
  } catch (err) {
    const apiErr = toApiError(err)
    throw apiErr
  }
}

export async function createScheduleEvent(payload: Omit<ScheduleEvent, 'id'>): Promise<ScheduleEvent> {
  try {
    const res = await http.post<ScheduleEvent>('/schedule/events/', payload)
    return res.data
  } catch (err) {
    const apiErr = toApiError(err)
    throw apiErr
  }
}

export async function updateScheduleEvent(id: string, payload: Omit<ScheduleEvent, 'id'>): Promise<ScheduleEvent> {
  try {
    const res = await http.patch<ScheduleEvent>(`/schedule/events/${id}/`, payload)
    return res.data
  } catch (err) {
    const apiErr = toApiError(err)
    throw apiErr
  }
}

export async function deleteScheduleEvent(id: string): Promise<void> {
  try {
    await http.delete(`/schedule/events/${id}/`)
  } catch (err) {
    const apiErr = toApiError(err)
    throw apiErr
  }
}


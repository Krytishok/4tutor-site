import { defineStore } from 'pinia'
import { createLesson, deleteLesson, listLessons, updateLesson } from '../api/lessons'
import type { Lesson, ScheduleEvent } from '../types/domain'
import { toApiError } from '../api/http'

export const useScheduleStore = defineStore('schedule', {
  state: () => ({
    events: [] as ScheduleEvent[],
    loading: false,
    error: '' as string,
  }),
  actions: {
    seedForRole() {
      this.events = []
      this.error = ''
    },

    lessonToEvent(lesson: Lesson): ScheduleEvent {
      const tutorName = lesson.tutor
        ? `${lesson.tutor.first_name} ${lesson.tutor.last_name}`.trim() || lesson.tutor.email
        : undefined
      // Безопасное извлечение ID учеников (могут прийти как объекты UserBrief или как примитивы)
      const studentIds = lesson.students.map((s: any) => {
        if (typeof s === 'object' && s !== null && 'id' in s) return String(s.id)
        return String(s) // на случай, если сервер вернул просто число
      })
      return {
        id: String(lesson.id),
        groupType: studentIds.length > 1 ? 'group' : 'private',
        studentIds,
        subject: lesson.subject,
        startAt: lesson.start_time,
        endAt: lesson.end_time,
        tutorId: lesson.tutor ? String(lesson.tutor.id) : undefined,
        tutorName,
        meetingUrl: lesson.meeting_url ?? undefined,
        isRecurringWeekly: lesson.is_recurring_weekly,
        status: lesson.status,
      }
    },

    async loadEvents(params?: { from?: string; to?: string; weekdays_only?: boolean }) {
      this.loading = true
      this.error = ''
      try {
        const lessons = await listLessons(params)
        this.events = lessons.map((l) => this.lessonToEvent(l))
      } catch (err) {
        this.error = toApiError(err).message
      } finally {
        this.loading = false
      }
    },

    async createEvent(payload: Omit<ScheduleEvent, 'id'>) {
      this.error = ''
      const lesson = await createLesson({
        students: payload.studentIds.map(Number),
        subject: payload.subject,
        start_time: payload.startAt,
        end_time: payload.endAt,
        meeting_url: payload.meetingUrl ?? null,
        is_recurring_weekly: payload.isRecurringWeekly ?? false,
      })
      this.events.unshift(this.lessonToEvent(lesson))
    },

    async updateEvent(id: string, payload: Omit<ScheduleEvent, 'id'>) {
      this.error = ''
      const lesson = await updateLesson(Number(id), {
        students: payload.studentIds.map(Number),
        subject: payload.subject,
        start_time: payload.startAt,
        end_time: payload.endAt,
        meeting_url: payload.meetingUrl ?? null,
        is_recurring_weekly: payload.isRecurringWeekly ?? false,
        status: payload.status,
      })
      const idx = this.events.findIndex((e) => e.id === id)
      if (idx >= 0) this.events[idx] = this.lessonToEvent(lesson)
    },

    async deleteEvent(id: string) {
      this.error = ''
      await deleteLesson(Number(id))
      this.events = this.events.filter((e) => e.id !== id)
    },
  },
  getters: {
    getEvents: (state) => state.events,
  },
})
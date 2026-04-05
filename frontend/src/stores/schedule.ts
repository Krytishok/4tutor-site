import { defineStore } from 'pinia'
import type { Role } from '../types/roles'
import type { ScheduleEvent } from '../types/domain'
import type { StudentGroupType } from '../types/domain'

function startOfWeekMonday(date: Date) {
  const d = new Date(date)
  const day = d.getDay() // 0=Sun ... 6=Sat
  const diff = (day === 0 ? -6 : 1) - day
  d.setDate(d.getDate() + diff)
  d.setHours(0, 0, 0, 0)
  return d
}

function withTime(date: Date, hours: number, minutes: number) {
  const d = new Date(date)
  d.setHours(hours, minutes, 0, 0)
  return d
}

export const useScheduleStore = defineStore('schedule', {
  state: () => ({
    events: [] as ScheduleEvent[],
  }),
  actions: {
    seedForRole(role: Role) {
      const weekStart = startOfWeekMonday(new Date())

      const make = (opts: {
        id: string
        groupType: StudentGroupType
        studentIds: string[]
        subject: string
        dayOffset: number
        startH: number
        startM: number
        endH: number
        endM: number
      }) => {
        const day = new Date(weekStart)
        day.setDate(day.getDate() + opts.dayOffset)
        return {
          id: opts.id,
          groupType: opts.groupType,
          studentIds: opts.studentIds,
          subject: opts.subject,
          startAt: withTime(day, opts.startH, opts.startM).toISOString(),
          endAt: withTime(day, opts.endH, opts.endM).toISOString(),
        } satisfies ScheduleEvent
      }

      // Demo data: tutor sees all students, student sees only their own.
      const tutorEvents = [
        make({
          id: 'e1',
          groupType: 'private',
          studentIds: ['s-anna'],
          subject: 'Алгебра',
          dayOffset: 0,
          startH: 18,
          startM: 0,
          endH: 19,
          endM: 0,
        }),
        make({
          id: 'e2',
          groupType: 'private',
          studentIds: ['s-ilya'],
          subject: 'Русский',
          dayOffset: 2,
          startH: 17,
          startM: 30,
          endH: 18,
          endM: 30,
        }),
        make({
          id: 'e3',
          groupType: 'group',
          studentIds: ['s-masha', 's-sergey'],
          subject: 'Английский',
          dayOffset: 4,
          startH: 19,
          startM: 0,
          endH: 20,
          endM: 0,
        }),
        make({
          id: 'e4',
          groupType: 'private',
          studentIds: ['s-anna'],
          subject: 'Геометрия',
          dayOffset: 1,
          startH: 16,
          startM: 0,
          endH: 17,
          endM: 0,
        }),
      ]

      const studentEvents =
        role === 'student'
          ? tutorEvents.filter((e) => e.studentIds.includes('s-anna') || e.studentIds.includes('s-ilya')).slice(0, 3)
          : tutorEvents

      this.events = role === 'student' ? studentEvents : tutorEvents
    },
    createEvent(payload: Omit<ScheduleEvent, 'id'>) {
      const id = `e-${Math.random().toString(16).slice(2, 8)}`
      this.events.push({ ...payload, id })

      // API (later):
      // await createScheduleEventApi(payload)
    },
    updateEvent(id: string, payload: Omit<ScheduleEvent, 'id'>) {
      const idx = this.events.findIndex((e) => e.id === id)
      if (idx === -1) return
      this.events[idx] = { ...this.events[idx], ...payload, id }

      // API (later):
      // await updateScheduleEventApi(id, payload)
    },
    deleteEvent(id: string) {
      this.events = this.events.filter((e) => e.id !== id)

      // API (later):
      // await deleteScheduleEventApi(id)
    },
  },
  getters: {
    getEvents: (state) => state.events,
  },
})


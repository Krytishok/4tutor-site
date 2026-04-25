import type { Role } from './roles'

export type ID = string

export type Person = {
  id: ID
  role: Role
  name: string
  email: string
}

export type Student = {
  id: ID
  name: string
  email: string
  subject?: string
}

export type AssignmentStatus = 'created' | 'submitted' | 'graded'

export type Assignment = {
  id: ID
  title: string
  text: string
  dueAt: string // ISO
  createdAt: string // ISO
  // For MVP attachments will be added later:
  // attachments: { id; filename; url }[]
}

export type AssignmentResult = {
  assignmentId: ID
  submittedAt?: string
  gradedAt?: string
  score?: number
  maxScore?: number
  comment?: string
}

export type HomeworkSubmission = {
  id: ID
  assignmentId: ID
  studentId: ID
  submittedAt: string // ISO
  answerText?: string
  // attachmentUrl?: string
}

export type ScheduleEvent = {
  id: ID
  groupType: StudentGroupType
  studentIds: ID[]
  subject: string
  startAt: string // ISO
  endAt: string // ISO
  tutorId?: ID
  tutorName?: string
  meetingUrl?: string
  isRecurringWeekly?: boolean
  status?: 'planned' | 'in_progress' | 'completed' | 'cancelled'
}

export type StudentGroupType = 'private' | 'group'

export type UserBrief = {
  id: number
  email: string
  first_name: string
  last_name: string
}

export type TutorStudentStatus = 'pending' | 'active' | 'rejected' | 'cancelled'

export type TutorStudentRelation = {
  id: number
  tutor: UserBrief
  student: UserBrief
  subject: string | null
  status: TutorStudentStatus
  created_at: string
}

export type LessonStatus = 'planned' | 'in_progress' | 'completed' | 'cancelled'

export type Lesson = {
  id: number
  tutor: UserBrief
  students: UserBrief[]
  subject: string
  start_time: string
  end_time: string
  status: LessonStatus
  meeting_url: string | null
  is_recurring_weekly: boolean
  created_at: string
  updated_at: string
}


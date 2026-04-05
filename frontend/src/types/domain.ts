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
  subject: string
  groupType: StudentGroupType
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
  studentIds: ID[] // 1 item for private, N items for group
  subject: string
  startAt: string // ISO
  endAt: string // ISO
  // tutorId: ID (in backend)
}

export type StudentGroupType = 'private' | 'group'


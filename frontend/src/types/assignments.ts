// src/types/assignments.ts

export interface Assignment {
  id: number
  tutor: { id: number; email: string; first_name: string; last_name: string }
  title: string
  description: string
  subject: string
  created_at: string
  updated_at: string
  files: AssignmentFile[]
  student_assignments: StudentAssignment[]
}

export interface AssignmentListItem {
  id: number
  tutor: { id: number; email: string; first_name: string; last_name: string }
  title: string
  subject: string
  created_at: string
  files_count: number
}

export interface AssignmentFile {
  id: number
  file: string // URL
  uploaded_at: string
}

export type StudentAssignmentStatus = 'assigned' | 'submitted' | 'graded'

export interface StudentAssignment {
  id: number
  assignment: number
  assignment_title?: string // для списка
  student: { id: number; email: string; first_name: string; last_name: string }
  deadline: string
  status: StudentAssignmentStatus
  grade: number | null
  tutor_comment: string
  submitted_at: string | null
  submission_files?: SubmissionFile[]
}

export interface StudentAssignmentListItem {
  id: number
  assignment: number
  assignment_title: string
  student: { id: number; email: string; first_name: string; last_name: string }
  deadline: string
  status: StudentAssignmentStatus
  grade: number | null
  submitted_at: string | null
}

export interface SubmissionFile {
  id: number
  file: string
  uploaded_at: string
}

export interface AssignStudentsPayload {
  assignments_data: { student_id: number; deadline: string }[]
}
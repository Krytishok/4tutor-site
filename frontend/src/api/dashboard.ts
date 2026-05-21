// src/api/dashboard.ts

import { http } from './http'

export interface TutorDeadlineItem {
  id: number
  assignment_title: string
  student_name: string
  deadline: string
  status: string
}

export interface TutorAssignmentStats {
  total_assignments: number
  active_assignments: number
  submitted_pending: number
  graded_count: number
}

export interface TutorRecentAssignment {
  id: number
  title: string
  subject: string
  created_at: string
  students_count: number
}

export interface TutorActiveStudent {
  id: number
  first_name: string
  last_name: string
  email: string
  pending_assignments_count: number
}

export interface TutorAttentionItem {
  id: number
  assignment_title: string
  student_name: string
  deadline: string
  status: string
  submitted_at: string | null
}

export interface TutorNeedsAttention {
  submitted_pending_count: number
  submitted_pending: TutorAttentionItem[]
  overdue_count: number
  overdue: TutorAttentionItem[]
}

export interface TutorDashboardData {
  upcoming_deadlines: TutorDeadlineItem[]
  assignment_stats: TutorAssignmentStats
  recent_assignments: TutorRecentAssignment[]
  active_students: TutorActiveStudent[]
  needs_attention: TutorNeedsAttention
}

export interface StudentActiveAssignment {
  id: number
  assignment_title: string
  tutor_name: string
  subject: string
  deadline: string
}

export interface StudentPendingGrade {
  id: number
  assignment_title: string
  submitted_at: string
  status: string
}

export interface StudentRecentGrade {
  id: number
  assignment_title: string
  grade: number
  tutor_comment: string
  submitted_at: string
}

export interface StudentStats {
  total_assignments: number
  completed_count: number
  average_grade: number
  progress_percentage: number
}

export interface StudentTutorItem {
  tutor_id: number
  tutor_name: string
  assignments_count: number
}

export interface StudentDashboardData {
  active_assignments: StudentActiveAssignment[]
  pending_grades: StudentPendingGrade[]
  recent_grades: StudentRecentGrade[]
  stats: StudentStats
  my_tutors: StudentTutorItem[]
}

// ---------- Dashboard API ----------

/**
 * Получить данные дашборда для репетитора
 */
export function getTutorDashboard(): Promise<TutorDashboardData> {
  return http.get<TutorDashboardData>('/v1/dashboard/tutor/').then(res => res.data)
}

/**
 * Получить данные дашборда для ученика
 */
export function getStudentDashboard(): Promise<StudentDashboardData> {
  return http.get<StudentDashboardData>('/v1/dashboard/student/').then(res => res.data)
}

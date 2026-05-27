// src/api/analytics.ts

import { http } from './http'

export interface AverageGradesChartItem {
  month: string
  avg_grade: number
}

export interface AssignmentCompletion {
  total: number
  assigned: number
  submitted: number
  graded: number
}

export interface StudentSummaryItem {
  id: number
  first_name: string
  last_name: string
  email: string
  average_grade: number | null
  completion_percentage: number
  progress_status: 'growing' | 'falling' | 'stable' | 'no_change'
  total_assignments: number
  completed_assignments: number
}

export interface TutorAnalyticsData {
  average_grades_chart: AverageGradesChartItem[]
  assignment_completion: AssignmentCompletion
  students_summary: StudentSummaryItem[]
}

export interface OverallStats {
  total_assignments: number
  average_grade: number
  completion_percentage: number
}

export interface StudentAnalyticsData {
  average_grades_chart: AverageGradesChartItem[]
  assignment_completion: AssignmentCompletion
  overall_stats: OverallStats
}

/**
 * Получить аналитику для репетитора
 */
export function getTutorAnalytics(): Promise<TutorAnalyticsData> {
  return http.get<TutorAnalyticsData>('/v1/analytics/tutor/').then(res => res.data)
}

/**
 * Получить аналитику для ученика
 */
export function getStudentAnalytics(): Promise<StudentAnalyticsData> {
  return http.get<StudentAnalyticsData>('/v1/analytics/student/').then(res => res.data)
}

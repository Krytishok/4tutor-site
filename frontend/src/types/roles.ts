export type Role = 'student' | 'tutor'

export const ROLE_LABEL: Record<Role, string> = {
  student: 'Ученик',
  tutor: 'Репетитор',
}

export type NavItem = { to: string; label: string }

export const ROLE_NAV: Record<Role, NavItem[]> = {
  tutor: [
    { to: '/app/tutor', label: 'Дашборд' },
    { to: '/app/tutor/students', label: 'Ученики' },
    { to: '/app/tutor/assignments', label: 'Задания' },
    { to: '/app/tutor/schedule', label: 'Расписание' },
    { to: '/app/tutor/reminders', label: 'Напоминания' },
    { to: '/app/tutor/analytics', label: 'Аналитика' },
  ],
  student: [
    { to: '/app/student/assignments', label: 'Мои задания' },
    { to: '/app/student/schedule', label: 'Моё расписание' },
    { to: '/app/student/results', label: 'Результаты' },
    { to: '/app/student/reminders', label: 'Напоминания' },
  ],
}


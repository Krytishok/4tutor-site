import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import AppShell from '../components/layout/AppShell.vue'
import LandingPage from '../pages/LandingPage.vue'
import LoginPage from '../pages/login/LoginPage.vue'
import RegisterPage from '../pages/RegisterPage.vue'
import NotFoundPage from '../pages/NotFoundPage.vue'
import TutorDashboardPage from '../pages/tutor/DashboardPage.vue'
import TutorStudentsPage from '../pages/tutor/StudentsPage.vue'
import TutorAssignmentsPage from '../pages/tutor/AssignmentsPage.vue'
import TutorSchedulePage from '../pages/tutor/SchedulePage.vue'
import TutorRemindersPage from '../pages/tutor/RemindersPage.vue'
import TutorAnalyticsPage from '../pages/tutor/AnalyticsPage.vue'
import StudentDashboardPage from '../pages/student/DashboardPage.vue'
import StudentAssignmentsPage from '../pages/student/AssignmentsPage.vue'
import StudentSchedulePage from '../pages/student/SchedulePage.vue'
import StudentInvitationsPage from '../pages/student/InvitationsPage.vue'
import StudentResultsPage from '../pages/student/ResultsPage.vue'
import StudentRemindersPage from '../pages/student/RemindersPage.vue'
import TutorAssignmentDetailPage from '../pages/tutor/AssignmentDetailPage.vue'
import StudentSubmissionReviewPage from '../pages/tutor/StudentSubmissionReviewPage.vue'
import StudentAssignmentDetailPage from '../pages/student/AssignmentDetailPage.vue'
import { useAuthStore } from '../stores/auth'
import { ROLE_NAV, type Role } from '../types/roles'

type AppRouteMeta = {
  requiresAuth?: boolean
  role?: Role
}

declare module 'vue-router' {
  interface RouteMeta extends AppRouteMeta {}
}

const routes: RouteRecordRaw[] = [
  { path: '/', component: LandingPage },
  {
    path: '/login',
    component: LoginPage,
  },
  {
    path: '/register',
    component: RegisterPage,
  },
  {
    path: '/app',
    component: AppShell,
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: '/app/tutor' },
      {
        path: 'tutor',
        component: TutorDashboardPage,
        meta: { requiresAuth: true, role: 'tutor' },
      },
      {
        path: 'tutor/students',
        component: TutorStudentsPage,
        meta: { requiresAuth: true, role: 'tutor' },
      },
      {
        path: 'tutor/assignments/:id',
        component: TutorAssignmentDetailPage,
        meta: { requiresAuth: true, role: 'tutor' },
      },
      {
        path: 'tutor/submissions/:pk',
        component: StudentSubmissionReviewPage,
        meta: { requiresAuth: true, role: 'tutor' },
      },
      {
        path: 'tutor/assignments',
        component: TutorAssignmentsPage,
        meta: { requiresAuth: true, role: 'tutor' },
      },
      {
        path: 'tutor/schedule',
        component: TutorSchedulePage,
        meta: { requiresAuth: true, role: 'tutor' },
      },
      {
        path: 'tutor/reminders',
        component: TutorRemindersPage,
        meta: { requiresAuth: true, role: 'tutor' },
      },
      {
        path: 'tutor/analytics',
        component: TutorAnalyticsPage,
        meta: { requiresAuth: true, role: 'tutor' },
      },
      {
        path: 'student',
        component: StudentDashboardPage,
        meta: { requiresAuth: true, role: 'student' },
      },

      {
        path: 'student/invitations',
        component: StudentInvitationsPage,
        meta: { requiresAuth: true, role: 'student' },
      },
      {
        path: 'student/assignments/:id',
        component: StudentAssignmentDetailPage,
        meta: { requiresAuth: true, role: 'student' },
      },
      {
        path: 'student/assignments',
        component: StudentAssignmentsPage,
        meta: { requiresAuth: true, role: 'student' },
      },
      
      {
        path: 'student/schedule',
        component: StudentSchedulePage,
        meta: { requiresAuth: true, role: 'student' },
      },
      {
        path: 'student/results',
        component: StudentResultsPage,
        meta: { requiresAuth: true, role: 'student' },
      },
      {
        path: 'student/reminders',
        component: StudentRemindersPage,
        meta: { requiresAuth: true, role: 'student' },
      },

      {
        path: 'student/redirect',
        redirect: '/app/student/assignments',
      },

      // Fallback inside /app
      { path: ':pathMatch(.*)*', redirect: '/login' },
    ],
  },
  { path: '/:pathMatch(.*)*', component: NotFoundPage },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

function roleToDefaultPath(role: Role): string {
  return ROLE_NAV[role]?.[0]?.to ?? `/app/${role}`
}

router.beforeEach((to) => {
  const auth = useAuthStore()
  const requiresAuth = to.meta.requiresAuth === true
  const targetRole = to.meta.role as Role | undefined

  if ((to.path === '/login' || to.path === '/register') && auth.isAuthed && auth.role) {
    return roleToDefaultPath(auth.role)
  }

  if (requiresAuth && !auth.isAuthed) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }

  if (targetRole && auth.role && targetRole !== auth.role) {
    return roleToDefaultPath(auth.role)
  }

  return true
})

export default router


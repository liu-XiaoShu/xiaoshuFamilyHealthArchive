// 修改后的路由配置代码
import { createRouter, createWebHistory } from 'vue-router'
import { getToken } from '../utils/auth'
import HomePage from '../views/HomePage.vue'
import LoginPage from '../views/LoginPage.vue'
import RegisterPage from '../views/RegisterPage.vue'
import DashboardPage from '@/views/DashboardPage.vue'
import NotFoundPage from '../views/NotFoundPage.vue'
import Home from '@/views/Home.vue'
import Login from '@/views/auth/Login.vue'
import Register from '@/views/auth/Register.vue'
import MedicalRecords from '@/views/records/MedicalRecords.vue'
import MedicationRecords from '@/views/records/MedicationRecords.vue'
import VaccinationRecords from '@/views/records/VaccinationRecords.vue'
import PhysicalExams from '@/views/records/PhysicalExams.vue'
import PhysicalExamReport from '@/views/records/PhysicalExamReport.vue'
import MedicalRecordForm from '@/views/records/MedicalRecordForm.vue'
import MedicationRecordForm from '@/views/records/MedicationRecordForm.vue'
import VaccinationRecordForm from '@/views/records/VaccinationRecordForm.vue'
import PhysicalExamForm from '@/views/records/PhysicalExamForm.vue'
import Profile from '@/views/user/Profile.vue'
import Settings from '@/views/user/Settings.vue'
import Health from '@/views/Health.vue'
import Test from '@/views/Test.vue'

// 不需要认证的路由
const publicRoutes = ['/login', '/register', '/forgot-password', '/health', '/test']

// 路由配置
const routes = [
  {
    path: '/',
    name: 'home',
    component: HomePage,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'login',
    component: LoginPage,
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterPage,
    meta: { requiresAuth: false }
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: DashboardPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('../views/user/Profile.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/medical-records',
    name: 'medical-records',
    component: () => import('../views/records/MedicalRecords.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/medication-records',
    name: 'medication-records',
    component: () => import('../views/records/MedicationRecords.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/vaccination-records',
    name: 'vaccination-records',
    component: () => import('../views/records/VaccinationRecords.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/physical-exams',
    name: 'physical-exams',
    component: () => import('../views/records/PhysicalExams.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: NotFoundPage
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 全局前置守卫
router.beforeEach((to, from, next) => {
  // 添加调试信息
  console.log('路由跳转:', from.path, '->', to.path)
  
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const hasToken = !!getToken()

  console.log('需要认证:', requiresAuth)
  console.log('有token:', hasToken)

  if (requiresAuth && !hasToken) {
    console.log('无权限访问，重定向到登录页')
    next('/login')
  } else {
    console.log('允许访问')
    next()
  }
})

export default router

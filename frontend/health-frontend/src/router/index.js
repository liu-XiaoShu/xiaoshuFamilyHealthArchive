// 修改后的路由配置代码
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
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
    redirect: '/login'
  },
  {
    path: '/home',
    name: 'home',
    component: Home,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'register',
    component: Register,
    meta: { requiresAuth: false }
  },
  // 就医记录路由
  {
    path: '/records/medical',
    name: 'medical-records',
    component: MedicalRecords,
    meta: { requiresAuth: true }
  },
  {
    path: '/records/medical/new',
    name: 'medical-record-new',
    component: MedicalRecordForm,
    meta: { requiresAuth: true }
  },
  {
    path: '/records/medical/:id/edit',
    name: 'medical-record-edit',
    component: MedicalRecordForm,
    meta: { requiresAuth: true }
  },
  // 用药记录路由
  {
    path: '/records/medication',
    name: 'medication-records',
    component: MedicationRecords,
    meta: { requiresAuth: true }
  },
  {
    path: '/records/medication/new',
    name: 'medication-record-new',
    component: MedicationRecordForm,
    meta: { requiresAuth: true }
  },
  {
    path: '/records/medication/:id/edit',
    name: 'medication-record-edit',
    component: MedicationRecordForm,
    meta: { requiresAuth: true }
  },
  // 疫苗接种路由
  {
    path: '/records/vaccination',
    name: 'vaccination-records',
    component: VaccinationRecords,
    meta: { requiresAuth: true }
  },
  {
    path: '/records/vaccination/new',
    name: 'vaccination-record-new',
    component: VaccinationRecordForm,
    meta: { requiresAuth: true }
  },
  {
    path: '/records/vaccination/:id/edit',
    name: 'vaccination-record-edit',
    component: VaccinationRecordForm,
    meta: { requiresAuth: true }
  },
  // 体检记录路由
  {
    path: '/records/physical',
    name: 'physical-exams',
    component: PhysicalExams,
    meta: { requiresAuth: true }
  },
  {
    path: '/records/physical/new',
    name: 'physical-exam-new',
    component: PhysicalExamForm,
    meta: { requiresAuth: true }
  },
  {
    path: '/records/physical/:id/edit',
    name: 'physical-exam-edit',
    component: PhysicalExamForm,
    meta: { requiresAuth: true }
  },
  {
    path: '/records/physical/:id/report',
    name: 'physical-exam-report',
    component: PhysicalExamReport,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'profile',
    component: Profile,
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'settings',
    component: Settings,
    meta: { requiresAuth: true }
  },
  {
    path: '/health',
    name: 'health',
    component: Health,
    meta: { requiresAuth: false }
  },
  {
    path: '/test',
    name: 'test',
    component: Test,
    meta: { requiresAuth: false }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFound.vue'),
    meta: { title: '404' }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 增强的导航守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const isAuthRoute = publicRoutes.includes(to.path)

  // 详细调试信息
  console.log('路由导航详情:', {
    目标路径: to.path,
    来源路径: from.path,
    需要认证: requiresAuth,
    是公开路由: isAuthRoute,
    当前认证状态: authStore.isAuthenticated,
    有认证Token: !!authStore.token,
    当前URL: window.location.href
  })

  // 特殊处理健康检查页面 - 始终允许访问
  if (to.path === '/health') {
    console.log('健康检查页面，无需认证直接访问')
    return next()
  }

  // 情况1：未登录用户访问需要认证的页面
  if (requiresAuth && !authStore.isAuthenticated) {
    console.log('未登录用户尝试访问需要认证的页面')
    return next({ path: '/login', query: { redirect: to.fullPath } })
  }

  // 情况2：已登录用户访问登录页或注册页
  if (authStore.isAuthenticated && (to.path === '/login' || to.path === '/register')) {
    console.log('已登录用户尝试访问登录页或注册页')
    return next({ path: '/home' })
  }

  next()
})

export default router

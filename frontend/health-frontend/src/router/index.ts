// 修改后的src/router/index.ts完整代码
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import type { RouteRecordRaw, RouteLocationNormalized, NavigationGuardNext } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import Login from '@/views/auth/Login.vue'
import Register from '@/views/auth/Register.vue'
import MedicalRecords from '@/views/records/MedicalRecords.vue'
import MedicationRecords from '@/views/records/MedicationRecords.vue'
import VaccinationRecords from '@/views/records/VaccinationRecords.vue'
import PhysicalExams from '@/views/records/PhysicalExams.vue'
import PhysicalExamReport from '@/views/records/PhysicalExamReport.vue'
import Profile from '@/views/user/Profile.vue'
import Settings from '@/views/user/Settings.vue'
import Health from '@/views/Health.vue'

// 不需要认证的路由
const publicRoutes = ['/login', '/register', '/forgot-password', '/health']

// 用户相关路由
const userRoutes = [
  {
    path: '/profile',
    name: 'profile',
    component: Profile,
    meta: {
      title: '个人资料',
      requiresAuth: true
    }
  },
  {
    path: '/avatar',
    name: 'avatar',
    component: () => import('@/views/user/AvatarManager.vue'),
    meta: {
      title: '头像管理',
      requiresAuth: true
    }
  }
]

// 路由配置
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('@/layout/index.vue'),
    children: [
      {
        path: '',
        name: 'home',
        component: HomeView,
        meta: {
          title: '首页',
          requiresAuth: true
        }
      },
      // 用户路由
      ...userRoutes,
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
      {
        path: '/medical-records',
        name: 'medical-records',
        component: MedicalRecords,
        meta: { requiresAuth: true }
      },
      {
        path: '/medication-records',
        name: 'medication-records',
        component: MedicationRecords,
        meta: { requiresAuth: true }
      },
      {
        path: '/vaccination-records',
        name: 'vaccination-records',
        component: VaccinationRecords,
        meta: { requiresAuth: true }
      },
      {
        path: '/physical-exams',
        name: 'physical-exams',
        component: PhysicalExams,
        meta: { requiresAuth: true }
      },
      {
        path: '/physical-exams/:id/report',
        name: 'physical-exam-report',
        component: PhysicalExamReport,
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
        path: '/:pathMatch(.*)*',
        name: 'not-found',
        component: () => import('@/views/NotFound.vue'),
        meta: { title: '404' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 强制重定向处理
function redirectToLogin(next: NavigationGuardNext) {
  console.log('强制重定向到登录页')
  next({ path: '/login', replace: true })
}

function redirectToHome(next: NavigationGuardNext) {
  console.log('已登录，强制重定向到首页')
  next({ path: '/', replace: true })
}

// 增强的导航守卫
router.beforeEach((to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) => {
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
    return redirectToLogin(next)
  }

  // 情况2：已登录用户访问登录页或注册页
  if (authStore.isAuthenticated && (to.path === '/login' || to.path === '/register')) {
    console.log('已登录用户尝试访问登录页或注册页')
    return redirectToHome(next)
  }

  // 情况3：根路径特殊处理
  if (to.path === '/' && !authStore.isAuthenticated) {
    console.log('未登录用户尝试访问根路径')
    return redirectToLogin(next)
  }

  // 其他情况正常导航
  console.log('导航至:', to.path)
  next()
})

export default router

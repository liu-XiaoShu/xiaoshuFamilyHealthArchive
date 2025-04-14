import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'

// 禁用Vue Devtools
window.__VUE_DEVTOOLS_GLOBAL_HOOK__ = { Vue: null }

// 添加全局错误处理
window.onerror = function(message, source, lineno, colno, error) {
  console.error('全局错误:', {
    message,
    source,
    lineno,
    colno,
    error
  })
  return false
}

console.log('开始初始化Vue应用...')

// 创建Vue应用实例
const app = createApp(App)

// 创建Pinia实例
const pinia = createPinia()

// 注册Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 使用插件
app.use(pinia)
app.use(router)
app.use(ElementPlus, {
  locale: zhCn
})

// 初始化认证状态
const authStore = useAuthStore()
authStore.initializeAuth()

// 添加错误处理
app.config.errorHandler = (err, vm, info) => {
  console.error('Vue错误:', err)
  console.error('错误信息:', info)
  console.error('组件:', vm)
}

// 添加警告处理
app.config.warnHandler = (msg, instance, trace) => {
  console.warn('Vue警告:', msg)
  console.warn('组件:', instance)
  console.warn('堆栈:', trace)
}

// 添加性能监控
if (import.meta.env.DEV) {
  const performance = window.performance
  if (performance) {
    performance.mark('app-start')
  }
}

// 挂载应用
console.log('开始挂载应用...')
app.mount('#app')

// 输出调试信息
console.log('应用已启动')
console.log('API URL:', import.meta.env.VITE_API_URL)
console.log('当前环境:', import.meta.env.MODE)
console.log('当前路由:', router.currentRoute.value.fullPath)
console.log('认证状态:', authStore.isAuthenticated)

// 监听路由变化
router.beforeEach((to, from, next) => {
  console.log('路由变化:', {
    to: to.path,
    from: from.path,
    requiresAuth: to.meta.requiresAuth,
    isAuthenticated: authStore.isAuthenticated
  })
  next()
})

// 记录性能指标
if (import.meta.env.DEV && performance) {
  performance.mark('app-mounted')
  performance.measure('app-load-time', 'app-start', 'app-mounted')
  const measures = performance.getEntriesByType('measure')
  console.log('性能指标:', measures)
}


<!-- src/App.vue -->
<template>
  <el-config-provider :locale="zhCn">
    <div class="app-container">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </div>
  </el-config-provider>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { ElConfigProvider } from 'element-plus'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import axios from 'axios'

const authStore = useAuthStore()
const router = useRouter()

onMounted(() => {
  console.log('======================')
  console.log('App组件挂载...')
  
  // 检查localStorage中的认证信息
  const storedToken = localStorage.getItem('token')
  const storedUser = localStorage.getItem('user')
  
  console.log('localStorage中存储的认证信息:', {
    token: storedToken ? '存在' : '不存在',
    user: storedUser ? '存在' : '不存在'
  })
  
  // 初始化认证状态
  console.log('调用initializeAuth初始化认证状态')
  authStore.initializeAuth()
  
  // 添加调试信息
  console.log('初始化后的认证状态:', {
    isAuthenticated: authStore.isAuthenticated,
    token: authStore.token ? '存在' : '不存在',
    user: authStore.user,
    currentPath: window.location.pathname
  })
  
  // 检查当前路径和认证状态
  const path = window.location.pathname
  
  console.log('当前路径检查:', path)
  
  // 特殊处理：只有健康检查页面不需要认证
  if (path === '/health') {
    console.log('正在访问健康检查页面，无需认证')
    return
  }
  
  // 如果用户已登录，确保axios头部设置了token
  if (authStore.isAuthenticated && authStore.token) {
    console.log('用户已登录，设置axios认证头部')
    axios.defaults.headers.common['Authorization'] = `Bearer ${authStore.token}`
  }
  
  // 如果用户未登录且不在登录相关页面，则重定向到登录页
  if (!authStore.isAuthenticated && 
      path !== '/login' && 
      path !== '/register' &&
      path !== '/forgot-password') {
    console.log('用户未登录，当前非登录相关页面，重定向到登录页')
    router.push('/login')
  } else {
    console.log('无需重定向，保持当前路径')
  }
  
  console.log('App组件挂载完成')
  console.log('======================')
})
</script>

<style>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  overflow: auto;
}

.app-container {
  height: 100vh;
  width: 100vw;
  margin: 0;
  padding: 0;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  overflow: auto;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 全局样式 */
* {
  box-sizing: border-box;
}

.el-main {
  padding: 20px;
  height: 100%;
}

.el-aside {
  transition: width 0.3s;
}

@media screen and (max-width: 768px) {
  .el-aside {
    width: 64px !important;
  }
}
</style>


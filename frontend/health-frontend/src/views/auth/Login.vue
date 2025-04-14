<template>
  <div class="login-container">
    <div class="login-background">
      <div class="circles">
        <div class="circle circle-1"></div>
        <div class="circle circle-2"></div>
        <div class="circle circle-3"></div>
        <div class="circle circle-4"></div>
      </div>
      <div class="pattern"></div>
    </div>
    
    <el-card class="login-card">
      <div class="login-header">
        <img src="@/assets/logo.svg" alt="Logo" class="logo" />
        <h2>小树家健康管理系统</h2>
        <p class="subtitle">您的健康，我们的关注</p>
      </div>
      
      <el-form
        ref="loginForm"
        :model="loginData"
        :rules="rules"
        label-position="top"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username" label="用户名">
          <el-input
            v-model="loginData.username"
            prefix-icon="User"
            placeholder="请输入用户名"
          />
        </el-form-item>

        <el-form-item prop="password" label="密码">
          <el-input
            v-model="loginData.password"
            type="password"
            prefix-icon="Lock"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>

        <div class="remember-forgot">
          <el-checkbox v-model="loginData.remember">记住我</el-checkbox>
          <el-link type="primary" @click="router.push('/forgot-password')">
            忘记密码？
          </el-link>
        </div>

        <el-button
          type="primary"
          native-type="submit"
          :loading="loading"
          class="login-button"
        >
          登录
        </el-button>

        <div class="register-link">
          还没有账号？
          <el-link type="primary" @click="router.push('/register')">
            立即注册
          </el-link>
        </div>
        
        <div class="health-check-link">
          <el-link type="info" @click="router.push('/health')">
            检查系统状态
          </el-link>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import type { LoginData } from '@/types/auth'
import axios from 'axios'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)
const loginForm = ref()

const loginData = reactive<LoginData>({
  username: '',
  password: '',
  remember: false
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度应在3-20个字符之间', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度应在6-20个字符之间', trigger: 'blur' }
  ]
}

onMounted(() => {
  console.log('登录页面已挂载')
  console.log('当前认证状态:', {
    isAuthenticated: authStore.isAuthenticated,
    token: authStore.token,
    user: authStore.user
  })
  
  // 如果已经登录，重定向到首页
  if (authStore.isAuthenticated) {
    console.log('用户已登录，重定向到首页')
    router.push('/')
  }
})

const handleLogin = async () => {
  if (!loginForm.value) return
  
  console.log('----------------------')
  console.log('开始登录过程')
  console.log('表单实例:', !!loginForm.value)
  console.log('初始认证状态:', {
    isAuthenticated: authStore.isAuthenticated,
    token: authStore.token ? '存在' : '不存在'
  })
  
  try {
    loading.value = true
    await loginForm.value.validate()
    
    console.log('表单验证通过')
    console.log('提交登录请求:', loginData)
    
    // 清除localStorage中可能存在的旧数据
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('user')
    console.log('已清除localStorage旧数据')
    
    // 登录请求
    await authStore.login({
      username: loginData.username,
      password: loginData.password
    })
    
    // 登录后状态检查
    console.log('登录成功,认证状态:', {
      isAuthenticated: authStore.isAuthenticated,
      token: authStore.token ? '存在' : '不存在',
      user: authStore.user
    })
    
    ElMessage.success('登录成功')
    
    // 使用500ms的超时，确保状态完全更新
    setTimeout(() => {
      console.log('准备重定向到首页')
      console.log('当前认证状态:', {
        isAuthenticated: authStore.isAuthenticated,
        token: authStore.token ? '存在' : '不存在'
      })
      
      // 确保localStorage中有token
      const storedToken = localStorage.getItem('token')
      console.log('localStorage中的token:', storedToken ? '存在' : '不存在')
      
      // 重新初始化认证状态
      authStore.initializeAuth()
      
      // 手动设置axios头部
      if (authStore.token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${authStore.token}`
        console.log('已设置axios头部Authorization')
      }
      
      // 重定向到首页
      console.log('执行路由跳转')
      router.push({ path: '/', replace: true })
    }, 500)
  } catch (error: any) {
    console.error('登录错误:', error)
    const errorMsg = error.response?.data?.detail || 
                   authStore.error || 
                   '登录失败，请检查用户名和密码'
    console.log('显示错误消息:', errorMsg)
    ElMessage.error(errorMsg)
    
    // 清除可能存在的部分认证数据
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('user')
  } finally {
    loading.value = false
    console.log('登录过程结束')
    console.log('----------------------')
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, var(--el-color-primary-light-3), var(--el-color-primary));
}

.login-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
}

.circles {
  position: absolute;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 8s infinite;
}

.circle-1 {
  width: 300px;
  height: 300px;
  left: -100px;
  top: -100px;
  animation-delay: 0s;
}

.circle-2 {
  width: 200px;
  height: 200px;
  right: -50px;
  top: 30%;
  animation-delay: 2s;
}

.circle-3 {
  width: 150px;
  height: 150px;
  left: 30%;
  bottom: 20%;
  animation-delay: 4s;
}

.circle-4 {
  width: 250px;
  height: 250px;
  right: 10%;
  bottom: -100px;
  animation-delay: 6s;
}

.pattern {
  position: absolute;
  width: 100%;
  height: 100%;
  background-image: url('@/assets/health-bg.svg');
  background-size: 100px;
  opacity: 0.1;
}

.login-card {
  width: 400px;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  position: relative;
  z-index: 1;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.logo {
  width: 80px;
  height: 80px;
  margin-bottom: 16px;
}

.login-header h2 {
  margin: 0;
  font-size: 24px;
  color: var(--el-text-color-primary);
}

.subtitle {
  margin: 8px 0 0;
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.remember-forgot {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.login-button {
  width: 100%;
  padding: 12px;
  font-size: 16px;
}

.register-link {
  margin-top: 16px;
  text-align: center;
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.health-check-link {
  margin-top: 12px;
  text-align: center;
  font-size: 12px;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) rotate(0);
  }
  50% {
    transform: translateY(-20px) rotate(5deg);
  }
}

@media screen and (max-width: 768px) {
  .login-card {
    width: 90%;
    margin: 20px;
  }

  .circle {
    display: none;
  }
}
</style> 
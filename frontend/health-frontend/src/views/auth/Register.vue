<template>
  <div class="register-container">
    <div class="register-background">
      <div class="circles">
        <div class="circle circle-1"></div>
        <div class="circle circle-2"></div>
        <div class="circle circle-3"></div>
        <div class="circle circle-4"></div>
      </div>
      <div class="pattern"></div>
    </div>

    <el-card class="register-card">
      <div class="register-header">
        <img src="@/assets/logo.svg" alt="Logo" class="logo" />
        <h2>小树家健康管理系统</h2>
        <p class="subtitle">创建您的账户</p>
      </div>

      <el-form
        ref="registerForm"
        :model="registerData"
        :rules="rules"
        label-position="top"
        @submit.prevent="handleRegister"
      >
        <el-form-item prop="username" label="用户名">
          <el-input
            v-model="registerData.username"
            prefix-icon="User"
            placeholder="请输入用户名"
          />
        </el-form-item>

        <el-form-item prop="email" label="邮箱">
          <el-input
            v-model="registerData.email"
            prefix-icon="Message"
            placeholder="请输入邮箱"
          />
        </el-form-item>

        <el-form-item prop="phone" label="手机号">
          <el-input
            v-model="registerData.phone"
            prefix-icon="Phone"
            placeholder="请输入手机号"
          />
        </el-form-item>

        <el-form-item prop="password" label="密码">
          <el-input
            v-model="registerData.password"
            type="password"
            prefix-icon="Lock"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>

        <el-form-item prop="confirmPassword" label="确认密码">
          <el-input
            v-model="registerData.confirmPassword"
            type="password"
            prefix-icon="Lock"
            placeholder="请再次输入密码"
            show-password
          />
        </el-form-item>

        <el-button
          type="primary"
          native-type="submit"
          :loading="loading"
          class="register-button"
        >
          注册
        </el-button>

        <div class="login-link">
          已有账号？
          <el-link type="primary" @click="router.push('/login')">
            立即登录
          </el-link>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, var(--el-color-primary-light-3), var(--el-color-primary));
}

.register-background {
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

.register-card {
  width: 400px;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  position: relative;
  z-index: 1;
}

.register-header {
  text-align: center;
  margin-bottom: 30px;
}

.logo {
  width: 80px;
  height: 80px;
  margin-bottom: 16px;
}

.register-header h2 {
  margin: 0;
  font-size: 24px;
  color: var(--el-text-color-primary);
}

.subtitle {
  margin: 8px 0 0;
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.register-button {
  width: 100%;
  padding: 12px;
  font-size: 16px;
}

.login-link {
  margin-top: 16px;
  text-align: center;
  font-size: 14px;
  color: var(--el-text-color-secondary);
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
  .register-card {
    width: 90%;
    margin: 20px;
  }

  .circle {
    display: none;
  }
}
</style>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Message, Phone, Lock } from '@element-plus/icons-vue'
import type { RegisterData } from '@/types/auth'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api/auth'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)
const registerForm = ref()

const registerData = reactive<RegisterData>({
  username: '',
  email: '',
  phone: '',
  password: '',
  password_confirm: '',
  confirmPassword: ''
})

const validatePass2 = (rule: any, value: string, callback: any) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== registerData.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度应在3-20个字符之间', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度应在6-20个字符之间', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validatePass2, trigger: 'blur' }
  ]
}

const handleRegister = async () => {
  if (!registerForm.value) return
  
  try {
    loading.value = true
    await registerForm.value.validate()
    
    console.log('提交注册请求:', {
      username: registerData.username,
      email: registerData.email,
      phone: registerData.phone,
      password: registerData.password,
      password_confirm: registerData.confirmPassword
    })
    
    // 将confirmPassword的值同步到password_confirm
    registerData.password_confirm = registerData.confirmPassword || registerData.password;
    
    const response = await authApi.register({
      username: registerData.username,
      email: registerData.email,
      phone: registerData.phone,
      password: registerData.password,
      password_confirm: registerData.password_confirm
    })

    console.log('注册响应:', response.data)
    
    ElMessage.success('注册成功')
    // 使用setTimeout确保消息有足够时间显示
    setTimeout(() => {
      router.push('/login')
    }, 1500)
  } catch (error: any) {
    console.error('注册错误:', error)
    if (error.response && error.response.data) {
      // 显示API返回的具体错误信息
      const errorData = error.response.data
      if (typeof errorData === 'object') {
        // 如果错误是对象，尝试提取每个字段的错误
        const errorMessages = Object.entries(errorData)
          .map(([field, errors]) => {
            if (Array.isArray(errors)) {
              return `${field}: ${errors.join(', ')}`
            } else {
              return `${field}: ${errors}`
            }
          })
          .join('\n')
        ElMessage.error(errorMessages || '注册失败，请检查输入')
      } else {
        // 如果是字符串直接显示
        ElMessage.error(errorData.toString())
      }
    } else {
      ElMessage.error('注册失败，请重试')
    }
  } finally {
    loading.value = false
  }
}
</script> 
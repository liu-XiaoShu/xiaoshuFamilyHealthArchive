<template>
  <div class="register-container">
    <el-card class="register-card">
      <template #header>
        <h2 class="card-header">注册</h2>
      </template>
      
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-position="top"
        @submit.prevent="handleSubmit"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="formData.username"
            placeholder="请输入用户名"
            :prefix-icon="User"
          />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="formData.email"
            placeholder="请输入邮箱"
            :prefix-icon="Message"
          />
        </el-form-item>

        <el-form-item label="手机号码" prop="phone">
          <el-input
            v-model="formData.phone"
            placeholder="请输入手机号码（选填）"
            :prefix-icon="Phone"
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="formData.password"
            type="password"
            placeholder="请输入密码"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>

        <el-form-item label="确认密码" prop="password_confirm">
          <el-input
            v-model="formData.password_confirm"
            type="password"
            placeholder="请再次输入密码确认"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>

        <div class="form-actions">
          <el-button
            type="primary"
            native-type="submit"
            :loading="loading"
            class="submit-btn"
          >
            注册
          </el-button>
        </div>

        <div class="form-footer">
          <p>
            已有账号？
            <router-link to="/login">立即登录</router-link>
          </p>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Message, Phone } from '@element-plus/icons-vue'
import type { FormInstance } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const formRef = ref<FormInstance>()
const loading = ref(false)

const formData = reactive({
  username: '',
  email: '',
  phone: '',
  password: '',
  password_confirm: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度应在3-20个字符之间', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6个字符', trigger: 'blur' }
  ],
  password_confirm: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule: any, value: string, callback: (error?: Error) => void) => {
        if (value !== formData.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    loading.value = true
    
    const response = await authStore.register(formData)
    ElMessage.success('注册成功')
    
    router.push('/login')
  } catch (error: any) {
    console.error('注册失败:', error)
    
    if (error.response?.data) {
      const backendErrors = error.response.data
      
      if (typeof backendErrors === 'object' && !Array.isArray(backendErrors)) {
        const firstErrorField = Object.keys(backendErrors)[0]
        const firstErrorMessage = Array.isArray(backendErrors[firstErrorField])
          ? backendErrors[firstErrorField][0]
          : backendErrors[firstErrorField]
          
        ElMessage.error(`${firstErrorField}: ${firstErrorMessage}`)
      } else if (backendErrors.detail) {
        ElMessage.error(backendErrors.detail)
      } else {
        ElMessage.error('注册失败，请检查输入信息')
      }
    } else {
      ElMessage.error('注册失败，请检查输入信息')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f7fa;
  padding: 20px;
}

.register-card {
  width: 100%;
  max-width: 500px;
}

.card-header {
  text-align: center;
  margin: 0;
  color: var(--el-text-color-primary);
}

.form-actions {
  margin-top: 24px;
}

.submit-btn {
  width: 100%;
}

.form-footer {
  margin-top: 16px;
  text-align: center;
  color: var(--el-text-color-regular);
}

.form-footer a {
  color: var(--el-color-primary);
  text-decoration: none;
}

.form-footer a:hover {
  text-decoration: underline;
}
</style>

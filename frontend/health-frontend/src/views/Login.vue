<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <h2>登录</h2>
      </template>
      
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        @submit.prevent="handleSubmit"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            native-type="submit"
            :loading="authStore.loading"
            class="submit-btn"
          >
            登录
          </el-button>
        </el-form-item>

        <div class="form-footer">
          <router-link to="/register">还没有账号？立即注册</router-link>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import type { FormInstance } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const authStore = useAuthStore()
const formRef = ref<FormInstance>()

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, message: '用户名至少3个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6个字符', trigger: 'blur' }
  ]
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    await authStore.login(form.username, form.password)
    ElMessage.success('登录成功')
  } catch (error: any) {
    ElMessage.error(error || '登录失败')
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1890ff11 0%, #1890ff22 100%);
  position: relative;
  overflow: hidden;
}

.login-container::before {
  content: "";
  position: absolute;
  width: 200%;
  height: 200%;
  background: url('@/assets/health-bg.svg');
  opacity: 0.1;
  animation: bg-move 20s linear infinite;
}

@keyframes bg-move {
  0% { transform: translateX(0) translateY(0); }
  100% { transform: translateX(-50%) translateY(-50%); }
}

.login-card {
  width: 420px;
  padding: 40px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 1;
}

.title {
  font-size: 28px;
  color: #1890ff;
  text-align: center;
  margin-bottom: 30px;
  font-weight: bold;
}

.form-item {
  margin-bottom: 24px;
}

.login-button {
  width: 100%;
  height: 40px;
  margin-top: 10px;
}

.register-link {
  text-align: center;
  margin-top: 16px;
  color: #666;
}

.register-link a {
  color: #1890ff;
  text-decoration: none;
}

.register-link a:hover {
  text-decoration: underline;
}

.submit-btn {
  width: 100%;
}

.form-footer {
  text-align: center;
  margin-top: 20px;
}

.form-footer a {
  color: var(--el-color-primary);
  text-decoration: none;
}

.form-footer a:hover {
  text-decoration: underline;
}
</style>


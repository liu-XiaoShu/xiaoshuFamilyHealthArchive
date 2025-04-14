<template>
  <div class="login-container">
    <el-card class="login-card">
      <div class="login-header">
        <h2>登录</h2>
      </div>
      <el-form
        ref="loginForm"
        :model="loginForm"
        :rules="loginRules"
        label-width="100px"
        class="login-form"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="loginForm.username" placeholder="请输入用户名"></el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="loginForm.password"
            placeholder="请输入密码"
            type="password"
            show-password
          ></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleLogin" :loading="loading">登录</el-button>
          <el-button @click="goToRegister">注册</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login } from '../api/auth'
import { setToken } from '../utils/auth'

export default {
  name: 'LoginPage',
  setup() {
    const router = useRouter()
    const loginForm = reactive({
      username: '',
      password: ''
    })
    const loginRules = {
      username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
      password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
    }
    const loginFormRef = ref(null)
    const loading = ref(false)

    const handleLogin = async () => {
      try {
        if (loginFormRef.value) {
          await loginFormRef.value.validate()
        }
        
        loading.value = true
        console.log('开始登录请求')
        
        try {
          const response = await login(loginForm.username, loginForm.password)
          console.log('登录成功', response)
          
          if (response.access) {
            setToken(response.access)
            ElMessage.success('登录成功')
            router.push('/')
          } else {
            throw new Error('未获取到访问令牌')
          }
        } catch (error) {
          console.error('登录请求错误:', error)
          ElMessage.error(error.response?.data?.detail || '登录失败，请检查用户名和密码')
        }
      } catch (formError) {
        console.error('表单验证错误:', formError)
      } finally {
        loading.value = false
      }
    }

    const goToRegister = () => {
      router.push('/register')
    }

    return {
      loginForm,
      loginRules,
      loginFormRef,
      loading,
      handleLogin,
      goToRegister
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f0f2f5;
}

.login-card {
  width: 400px;
}

.login-header {
  text-align: center;
  margin-bottom: 20px;
}

.login-form {
  padding: 0 20px;
}
</style> 
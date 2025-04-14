<template>
  <div class="register-container">
    <el-card class="register-card">
      <div class="register-header">
        <h2>用户注册</h2>
      </div>
      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="registerRules"
        label-width="100px"
        class="register-form"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="registerForm.username" placeholder="请输入用户名"></el-input>
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="registerForm.email" placeholder="请输入邮箱"></el-input>
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input v-model="registerForm.name" placeholder="请输入姓名"></el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="registerForm.password"
            placeholder="请输入密码"
            type="password"
            show-password
          ></el-input>
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            placeholder="请再次输入密码"
            type="password"
            show-password
          ></el-input>
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-select v-model="registerForm.gender" placeholder="请选择性别">
            <el-option label="男" value="M"></el-option>
            <el-option label="女" value="F"></el-option>
            <el-option label="其他" value="O"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="出生日期" prop="birth_date">
          <el-date-picker
            v-model="registerForm.birth_date"
            type="date"
            placeholder="选择日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          ></el-date-picker>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleRegister" :loading="loading">注册</el-button>
          <el-button @click="goToLogin">返回登录</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { register } from '../api/auth'

export default {
  name: 'RegisterPage',
  setup() {
    const router = useRouter()
    const registerFormRef = ref(null)
    const loading = ref(false)
    
    const registerForm = reactive({
      username: '',
      email: '',
      name: '',
      password: '',
      confirmPassword: '',
      gender: '',
      birth_date: ''
    })
    
    const validatePass = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请输入密码'))
      } else {
        if (registerForm.confirmPassword !== '') {
          if (registerFormRef.value) {
            registerFormRef.value.validateField('confirmPassword')
          }
        }
        callback()
      }
    }
    
    const validatePass2 = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请再次输入密码'))
      } else if (value !== registerForm.password) {
        callback(new Error('两次输入密码不一致!'))
      } else {
        callback()
      }
    }
    
    const registerRules = {
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
      ],
      email: [
        { required: true, message: '请输入邮箱地址', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
      ],
      name: [
        { required: true, message: '请输入姓名', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, message: '密码长度不能小于6位', trigger: 'blur' },
        { validator: validatePass, trigger: 'blur' }
      ],
      confirmPassword: [
        { required: true, message: '请再次输入密码', trigger: 'blur' },
        { validator: validatePass2, trigger: 'blur' }
      ],
      gender: [
        { required: true, message: '请选择性别', trigger: 'change' }
      ],
      birth_date: [
        { required: true, message: '请选择出生日期', trigger: 'change' }
      ]
    }
    
    const handleRegister = async () => {
      try {
        if (registerFormRef.value) {
          await registerFormRef.value.validate()
        }
        
        loading.value = true
        console.log('开始注册请求')
        
        // 构建注册数据，移除确认密码
        const registerData = { ...registerForm }
        delete registerData.confirmPassword
        
        try {
          const response = await register(registerData)
          console.log('注册成功', response)
          ElMessage.success('注册成功，请登录')
          router.push('/login')
        } catch (error) {
          console.error('注册请求错误:', error)
          if (error.response?.data) {
            // 处理后端返回的验证错误
            const errorData = error.response.data
            let errorMsg = '注册失败: '
            
            for (const key in errorData) {
              errorMsg += `${key}: ${errorData[key].join(', ')}; `
            }
            
            ElMessage.error(errorMsg)
          } else {
            ElMessage.error('注册失败，请稍后再试')
          }
        }
      } catch (formError) {
        console.error('表单验证错误:', formError)
      } finally {
        loading.value = false
      }
    }
    
    const goToLogin = () => {
      router.push('/login')
    }
    
    return {
      registerForm,
      registerRules,
      registerFormRef,
      loading,
      handleRegister,
      goToLogin
    }
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 20px 0;
  background-color: #f0f2f5;
}

.register-card {
  width: 500px;
}

.register-header {
  text-align: center;
  margin-bottom: 20px;
}

.register-form {
  padding: 0 20px;
}
</style> 
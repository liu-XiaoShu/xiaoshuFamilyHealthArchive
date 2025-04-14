<template>
  <div class="register-container">
    <el-card class="register-card">
      <template #header>
        <h2 class="register-title">注册</h2>
      </template>
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="0"
        @keyup.enter="handleSubmit"
      >
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名"
            prefix-icon="User"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        <el-form-item prop="password2">
          <el-input
            v-model="form.password2"
            type="password"
            placeholder="确认密码"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        <el-form-item prop="email">
          <el-input
            v-model="form.email"
            placeholder="邮箱"
            prefix-icon="Message"
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            :loading="loading"
            class="submit-btn"
            @click="handleSubmit"
          >
            注册
          </el-button>
        </el-form-item>
        <div class="form-footer">
          <router-link to="/login">已有账号？立即登录</router-link>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'
import { User, Lock, Message } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

export default defineComponent({
  name: 'RegisterView',
  components: {
    User,
    Lock,
    Message
  },
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const formRef = ref<FormInstance>()
    const loading = ref(false)
    const form = ref({
      username: '',
      password: '',
      password2: '',
      email: ''
    })

    const validatePass = (rule: any, value: string, callback: any) => {
      if (value === '') {
        callback(new Error('请输入密码'))
      } else {
        if (form.value.password2 !== '') {
          if (formRef.value) {
            formRef.value.validateField('password2')
          }
        }
        callback()
      }
    }

    const validatePass2 = (rule: any, value: string, callback: any) => {
      if (value === '') {
        callback(new Error('请再次输入密码'))
      } else if (value !== form.value.password) {
        callback(new Error('两次输入密码不一致!'))
      } else {
        callback()
      }
    }

    const rules = {
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
      ],
      password: [
        { required: true, validator: validatePass, trigger: 'blur' },
        { min: 6, message: '密码长度至少为 6 个字符', trigger: 'blur' }
      ],
      password2: [
        { required: true, validator: validatePass2, trigger: 'blur' }
      ],
      email: [
        { required: true, message: '请输入邮箱地址', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
      ]
    }

    const handleSubmit = async () => {
      if (!formRef.value) return

      try {
        await formRef.value.validate()
        loading.value = true
        await authStore.register(form.value)
        ElMessage.success('注册成功')
        router.push('/login')
      } catch (error) {
        console.error('注册失败:', error)
        ElMessage.error('注册失败，请检查输入信息')
      } finally {
        loading.value = false
      }
    }

    return {
      formRef,
      form,
      rules,
      loading,
      handleSubmit
    }
  }
})
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.register-card {
  width: 100%;
  max-width: 400px;
}

.register-title {
  text-align: center;
  margin: 0;
  font-size: 24px;
  color: var(--el-text-color-primary);
}

.submit-btn {
  width: 100%;
}

.form-footer {
  text-align: center;
  margin-top: 16px;
}

.form-footer a {
  color: var(--el-color-primary);
  text-decoration: none;
}

.form-footer a:hover {
  text-decoration: underline;
}
</style> 
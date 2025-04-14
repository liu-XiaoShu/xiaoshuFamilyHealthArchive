<template>
  <div class="home-container">
    <el-card class="welcome-card">
      <h1>欢迎使用小树家健康管理系统</h1>
      <p>请登录以继续使用系统</p>
      <el-button type="primary" @click="goToLogin">去登录</el-button>
    </el-card>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'

export default {
  name: 'HomePage',
  setup() {
    const router = useRouter()
    
    const goToLogin = () => {
      router.push('/login')
    }
    
    return {
      goToLogin
    }
  }
}
</script>

<style scoped>
.home-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.welcome-card {
  width: 500px;
  text-align: center;
  padding: 40px;
}

.welcome-card h1 {
  margin-bottom: 20px;
  color: #409EFF;
}

.welcome-card p {
  margin-bottom: 30px;
  color: #606266;
}
</style> 
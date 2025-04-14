<template>
  <div class="health-check">
    <h1>小树家健康管理系统状态</h1>
    <div v-if="loading" class="loading">
      <el-progress type="circle" :percentage="loadingProgress" />
      <p>正在检查系统状态...</p>
    </div>
    <div v-else class="health-status">
      <el-result
        :icon="healthStatus.status === 'healthy' ? 'success' : 'error'"
        :title="healthStatus.status === 'healthy' ? '系统正常' : '系统异常'"
        :sub-title="healthStatus.message"
      >
        <template #extra>
          <div class="action-buttons">
            <el-button type="primary" @click="checkHealth">重新检查</el-button>
            <el-button @click="goToLogin">前往登录</el-button>
          </div>
        </template>
      </el-result>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { healthCheck } from '@/api/index'

const router = useRouter()
const loading = ref(true)
const loadingProgress = ref(0)
const healthStatus = ref({
  status: 'unknown',
  message: '尚未检查'
})

// 导航到登录页面
const goToLogin = () => {
  console.log('导航到登录页面')
  router.push('/login')
}

const checkHealth = async () => {
  loading.value = true
  loadingProgress.value = 0
  
  // 模拟进度条
  const interval = setInterval(() => {
    if (loadingProgress.value < 90) {
      loadingProgress.value += 10
    }
  }, 200)
  
  try {
    const status = await healthCheck()
    healthStatus.value = status
    console.log('健康检查结果:', status)
  } catch (error) {
    console.error('健康检查发生错误:', error)
    healthStatus.value = {
      status: 'unhealthy',
      message: '检查过程中发生错误'
    }
  } finally {
    loadingProgress.value = 100
    clearInterval(interval)
    setTimeout(() => {
      loading.value = false
    }, 500)
  }
}

onMounted(() => {
  console.log('健康检查页面已挂载')
  checkHealth()
})
</script>

<style scoped>
.health-check {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
}

.health-status {
  margin-top: 20px;
}

.action-buttons {
  display: flex;
  gap: 12px;
  justify-content: center;
}
</style> 
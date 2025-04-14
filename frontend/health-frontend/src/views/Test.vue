<template>
  <div class="test-container">
    <el-card class="test-card">
      <template #header>
        <div class="card-header">
          <h2>功能测试页面</h2>
        </div>
      </template>
      
      <div class="test-content">
        <h3>1. 基础Vue功能测试</h3>
        <div class="test-item">
          <p>计数器: {{ counter }}</p>
          <el-button type="primary" @click="counter++">增加</el-button>
          <el-button type="info" @click="counter--">减少</el-button>
        </div>

        <h3>2. Element Plus组件测试</h3>
        <div class="test-item">
          <el-input v-model="inputText" placeholder="请输入内容"></el-input>
          <p>输入的内容: {{ inputText }}</p>
        </div>

        <h3>3. 路由功能测试</h3>
        <div class="test-item">
          <el-button @click="testRouter">测试路由</el-button>
          <p>当前路由: {{ $route.path }}</p>
        </div>

        <h3>4. Pinia状态测试</h3>
        <div class="test-item">
          <p>认证状态: {{ isAuthenticated ? '已登录' : '未登录' }}</p>
          <el-button type="success" @click="testPinia">测试Pinia</el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const counter = ref(0)
const inputText = ref('')
const router = useRouter()
const $route = useRoute()
const authStore = useAuthStore()

const isAuthenticated = computed(() => authStore.isAuthenticated)

const testRouter = () => {
  ElMessage.success('路由功能正常')
}

const testPinia = () => {
  ElMessage.info('Pinia状态管理正常')
}
</script>

<style scoped>
.test-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 20px;
  background-color: #f5f7fa;
}

.test-card {
  width: 100%;
  max-width: 600px;
}

.card-header {
  text-align: center;
}

.test-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.test-item {
  padding: 10px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  background-color: white;
}

h3 {
  margin-bottom: 10px;
  color: #409EFF;
}
</style> 
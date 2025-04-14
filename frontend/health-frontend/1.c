<template>
  <el-container>
    <el-header height="60px">
      <div class="nav-container">
        <router-link to="/records">健康记录</router-link>
        <el-button
          v-if="isAuthenticated"
          type="danger"
          @click="handleLogout"
        >
          退出登录
        </el-button>
      </div>
    </el-header>
    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const isAuthenticated = computed(() => !!localStorage.getItem('access_token'))

const handleLogout = () => {
  authStore.logout()
  window.location.href = '/login'
}
</script>

<style scoped>
.nav-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  padding: 0 20px;
  background: #fff;
  box-shadow: 0 2px 4px rgba(0,0,0,.1);
}
</style>


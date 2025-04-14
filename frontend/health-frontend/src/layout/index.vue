<template>
  <el-container class="app-container">
    <!-- 主要内容区 -->
    <el-container>
      <!-- 顶部导航栏，只在用户已登录时显示 -->
      <el-header v-if="authStore.isAuthenticated" class="header">
        <div class="header-left">
          <div class="logo">
            <img src="@/assets/logo.svg" alt="Logo">
            <span>健康管理系统</span>
          </div>
          <el-menu mode="horizontal" :default-active="route.path" class="horizontal-menu" :router="true">
            <el-menu-item index="/">
              <el-icon><HomeFilled /></el-icon>首页
            </el-menu-item>
            <el-menu-item index="/medical-records">
              <el-icon><FirstAidKit /></el-icon>就医记录
            </el-menu-item>
            <el-menu-item index="/medication-records">
              <el-icon><Collection /></el-icon>用药记录
            </el-menu-item>
            <el-menu-item index="/vaccination-records">
              <el-icon><Stamp /></el-icon>疫苗接种
            </el-menu-item>
            <el-menu-item index="/physical-exams">
              <el-icon><List /></el-icon>体检记录
            </el-menu-item>
          </el-menu>
        </div>

        <div class="header-right">
          <el-dropdown trigger="click">
            <div class="avatar-container">
              <el-avatar :size="32" :src="userAvatar">
                {{ userName.charAt(0) }}
              </el-avatar>
              <span class="user-name">{{ userName }}</span>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="router.push('/profile')">
                  <el-icon><User /></el-icon>个人资料
                </el-dropdown-item>
                <el-dropdown-item @click="router.push('/settings')">
                  <el-icon><Setting /></el-icon>系统设置
                </el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">
                  <el-icon><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 内容区 -->
      <el-main class="main" :style="authStore.isAuthenticated ? {} : {padding: 0}">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  HomeFilled,
  Notebook,
  List,
  FirstAidKit,
  Collection,
  Stamp,
  User,
  Setting,
  Expand,
  Fold,
  SwitchButton
} from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const userAvatar = computed(() => {
  return authStore.user?.avatar || ''
})
const userName = computed(() => authStore.user?.username || '用户')

// 退出登录
const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await authStore.logout()
    router.push('/login')
  } catch {
    // 用户取消操作
  }
}
</script>

<style scoped>
.app-container {
  height: 100vh;
}

.header {
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 60px;
}

.header-left {
  display: flex;
  align-items: center;
  flex: 1;
}

.header-right {
  display: flex;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  margin-right: 20px;
}

.logo img {
  width: 32px;
  height: 32px;
  margin-right: 12px;
}

.logo span {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.horizontal-menu {
  border-bottom: none;
}

.avatar-container {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.user-name {
  margin-left: 8px;
  font-size: 14px;
}

.main {
  background-color: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
}

@media (max-width: 768px) {
  .user-name {
    display: none;
  }
  
  .horizontal-menu {
    overflow-x: auto;
  }
}
</style> 
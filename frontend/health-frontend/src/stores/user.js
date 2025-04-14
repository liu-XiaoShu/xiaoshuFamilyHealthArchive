import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useAuthStore } from './auth'

export const useUserStore = defineStore('user', () => {
  // 引用认证Store
  const authStore = useAuthStore()
  
  // 状态
  const profile = ref(null)
  const loading = ref(false)
  const error = ref(null)
  
  // 计算属性
  const username = computed(() => profile.value?.username || authStore.user?.username || '用户')
  const userId = computed(() => profile.value?.id || authStore.user?.id)
  const isProfileComplete = computed(() => !!profile.value && !!profile.value.phone)
  
  // 加载用户资料
  const loadUserProfile = async () => {
    if (!authStore.isAuthenticated) return null
    
    try {
      loading.value = true
      error.value = null
      
      // 模拟API请求
      await new Promise(resolve => setTimeout(resolve, 500))
      
      profile.value = {
        id: authStore.user?.id || 1,
        username: authStore.user?.username || '用户',
        email: authStore.user?.email || 'user@example.com',
        phone: '13800138000',
        birthDate: '1990-01-01',
        gender: '女',
        height: 165,
        weight: 55,
        bloodType: 'A',
        avatar: '/images/avatar.jpg'
      }
      
      return profile.value
    } catch (err) {
      console.error('加载用户资料失败:', err)
      error.value = '加载用户资料失败'
      return null
    } finally {
      loading.value = false
    }
  }
  
  // 更新用户资料
  const updateUserProfile = async (userData) => {
    if (!authStore.isAuthenticated) return false
    
    try {
      loading.value = true
      error.value = null
      
      // 模拟API请求
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // 更新资料
      profile.value = {
        ...profile.value,
        ...userData
      }
      
      return true
    } catch (err) {
      console.error('更新用户资料失败:', err)
      error.value = '更新用户资料失败'
      return false
    } finally {
      loading.value = false
    }
  }
  
  // 重置状态
  const resetUserState = () => {
    profile.value = null
    loading.value = false
    error.value = null
  }
  
  return {
    profile,
    loading,
    error,
    username,
    userId,
    isProfileComplete,
    loadUserProfile,
    updateUserProfile,
    resetUserState
  }
})

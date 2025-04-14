import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// 清除存储的认证信息
localStorage.removeItem('token')
localStorage.removeItem('user')

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const token = ref(localStorage.getItem('token') || null)
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const isAuthenticated = computed(() => !!token.value)

  // 初始化认证状态
  const initializeAuth = async () => {
    console.log('初始化认证状态')
    // 检查token的有效性
    if (token.value) {
      try {
        // 模拟API验证token
        console.log('验证token有效性')
        // 如果要从真实API获取，可以解除注释以下代码
        // const response = await fetch('/api/verify-token', {
        //   headers: {
        //     'Authorization': `Bearer ${token.value}`
        //   }
        // })
        // if (!response.ok) {
        //   throw new Error('Token无效')
        // }
        
        // 如果没有用户信息，尝试获取
        if (!user.value) {
          console.log('获取用户信息')
          // 模拟获取用户信息
          user.value = {
            id: 1,
            username: '刘述瑶',
            email: 'user@example.com'
          }
          localStorage.setItem('user', JSON.stringify(user.value))
        }
      } catch (error) {
        console.error('初始化认证失败:', error)
        // 清除无效凭据
        logout()
      }
    }
  }

  // 登录
  const login = async (credentials) => {
    try {
      console.log('尝试登录', credentials)
      // 模拟API登录
      // const response = await fetch('/api/login', {
      //   method: 'POST',
      //   headers: {
      //     'Content-Type': 'application/json'
      //   },
      //   body: JSON.stringify(credentials)
      // })
      // if (!response.ok) {
      //   throw new Error('登录失败')
      // }
      // const data = await response.json()
      
      // 使用模拟数据
      const data = {
        token: 'fake-jwt-token',
        user: {
          id: 1,
          username: '刘述瑶',
          email: credentials.username || 'user@example.com'
        }
      }
      
      // 保存token和用户信息
      token.value = data.token
      user.value = data.user
      
      // 存储到本地存储
      localStorage.setItem('token', data.token)
      localStorage.setItem('user', JSON.stringify(data.user))
      
      return { success: true }
    } catch (error) {
      console.error('登录失败:', error)
      return { success: false, message: error.message }
    }
  }

  // 注册
  const register = async (userData) => {
    try {
      console.log('尝试注册', userData)
      // 模拟API注册
      // const response = await fetch('/api/register', {
      //   method: 'POST',
      //   headers: {
      //     'Content-Type': 'application/json'
      //   },
      //   body: JSON.stringify(userData)
      // })
      // if (!response.ok) {
      //   throw new Error('注册失败')
      // }
      // const data = await response.json()
      
      // 使用模拟数据
      const data = {
        token: 'fake-jwt-token',
        user: {
          id: 1,
          username: userData.username,
          email: userData.email
        }
      }
      
      // 保存token和用户信息
      token.value = data.token
      user.value = data.user
      
      // 存储到本地存储
      localStorage.setItem('token', data.token)
      localStorage.setItem('user', JSON.stringify(data.user))
      
      return { success: true }
    } catch (error) {
      console.error('注册失败:', error)
      return { success: false, message: error.message }
    }
  }

  // 退出登录
  const logout = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  return {
    token,
    user,
    isAuthenticated,
    initializeAuth,
    login,
    register,
    logout
  }
}) 
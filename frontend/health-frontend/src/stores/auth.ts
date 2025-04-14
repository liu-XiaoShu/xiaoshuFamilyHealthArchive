import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { userApi } from '@/api/user'

interface User {
  id: number
  username: string
  email: string
  phone: string
  avatar?: string
}

interface UserProfile {
  id: number
  user: number
  avatar: string | null
  birth_date: string | null
  gender: string | null
  address: string | null
}

interface LoginData {
  username: string
  password: string
}

interface RegisterData {
  username: string
  email: string
  phone: string
  password: string
}

// 修改API路径以匹配Django后端
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const refreshToken = ref<string | null>(localStorage.getItem('refreshToken'))
  const profile = ref<UserProfile | null>(null)
  const loading = ref<boolean>(false)
  const error = ref<string | null>(null)
  const router = useRouter()
  const isAuthenticated = computed(() => !!token.value)

  // 设置认证信息
  const setAuth = (userData: User, accessToken: string, newRefreshToken: string) => {
    user.value = userData
    token.value = accessToken
    refreshToken.value = newRefreshToken
    localStorage.setItem('token', accessToken)
    localStorage.setItem('refreshToken', newRefreshToken)
    localStorage.setItem('user', JSON.stringify(userData))
    // 设置axios默认headers
    axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`
  }

  // 清除认证信息
  const clearAuth = () => {
    user.value = null
    token.value = null
    refreshToken.value = null
    profile.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('user')
    delete axios.defaults.headers.common['Authorization']
  }

  // 初始化状态
  const initializeAuth = () => {
    console.log('开始初始化认证状态')
    const storedToken = localStorage.getItem('token')
    const storedUser = localStorage.getItem('user')
    
    console.log('从localStorage获取到的信息:', { 
      storedToken: storedToken ? '存在' : '不存在', 
      storedUser: storedUser ? '存在' : '不存在' 
    })
    
    if (storedToken) {
      token.value = storedToken
      console.log('设置令牌:', storedToken)
      axios.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`
      
      if (storedUser) {
        try {
          user.value = JSON.parse(storedUser)
          console.log('恢复用户信息成功:', user.value)
        } catch (e) {
          console.error('解析用户信息失败:', e)
          localStorage.removeItem('user')
        }
      }
      
      // 重新加载用户信息
      loadUser()
    } else {
      console.log('未找到存储的令牌，用户未登录')
    }
  }

  // 加载用户信息
  const loadUser = async () => {
    console.log('开始加载用户信息')
    try {
      const response = await axios.get(`${API_URL}/users/me/`, {
        headers: { Authorization: `Bearer ${token.value}` }
      })
      console.log('加载用户信息成功:', response.data)
      user.value = response.data
      
      // 检查并保存到localStorage
      localStorage.setItem('user', JSON.stringify(response.data))
      
      // 如果用户没有头像，尝试设置默认头像
      if (!response.data.avatar) {
        console.log('用户无头像，尝试设置默认头像')
        try {
          await userApi.setDefaultAvatar()
          // 设置成功后重新加载用户信息
          const updatedResponse = await axios.get(`${API_URL}/users/me/`, {
            headers: { Authorization: `Bearer ${token.value}` }
          })
          user.value = updatedResponse.data
          localStorage.setItem('user', JSON.stringify(updatedResponse.data))
        } catch (avatarError) {
          console.error('设置默认头像失败:', avatarError)
        }
      }
    } catch (error) {
      console.error('加载用户信息失败:', error)
      console.log('由于加载失败，执行登出操作')
      logout()
    }
  }

  // 登录
  const login = async (data: LoginData) => {
    try {
      loading.value = true
      error.value = null
      console.log('登录请求开始...')
      console.log('登录API地址:', `${API_URL}/users/login/`)
      console.log('登录数据:', data)
      
      // 确保token值为空
      token.value = null
      user.value = null
      delete axios.defaults.headers.common['Authorization']
      
      const response = await axios.post(`${API_URL}/users/login/`, data)
      console.log('登录响应:', response.data)
      
      // 检查响应格式
      if (!response.data.access || !response.data.refresh) {
        console.error('API响应格式错误，缺少access或refresh token')
        throw new Error('API响应格式错误')
      }
      
      const { access, refresh, user: userData } = response.data
      console.log('正在设置认证信息...')
      
      // 先存储到localStorage
      localStorage.setItem('token', access)
      localStorage.setItem('refreshToken', refresh)
      localStorage.setItem('user', JSON.stringify(userData))
      
      // 然后更新状态
      user.value = userData
      token.value = access
      refreshToken.value = refresh
      
      // 设置axios默认headers
      axios.defaults.headers.common['Authorization'] = `Bearer ${access}`
      
      console.log('登录完成，认证状态:', { 
        isAuthenticated: !!token.value,
        user: user.value 
      })
      
      // 检查用户是否有头像，如果没有则设置默认头像
      if (!userData.avatar) {
        console.log('用户无头像，尝试设置默认头像')
        try {
          await userApi.setDefaultAvatar()
          // 设置成功后重新加载用户信息
          await loadUser()
        } catch (avatarError) {
          console.error('设置默认头像失败:', avatarError)
        }
      }
      
      return response.data
    } catch (err: any) {
      console.error('登录失败:', err)
      console.log('错误响应:', err.response?.data)
      error.value = err.response?.data?.detail || '登录失败，请检查用户名和密码'
      
      // 清除可能部分设置的状态
      clearAuth()
      
      throw err
    } finally {
      loading.value = false
    }
  }

  // 注册
  const register = async (data: any) => {
    try {
      loading.value = true
      error.value = null
      console.log('注册请求开始...')
      console.log('注册API地址:', `${API_URL}/users/register/`)
      console.log('注册数据:', data)
      
      // 准备注册数据，只保留后端所需字段
      const registerData: {
        username: string;
        email: string;
        password: string;
        password_confirm: string;
        phone?: string;
      } = {
        username: data.username,
        email: data.email,
        password: data.password,
        password_confirm: data.password  // 后端需要密码确认字段
      }
      
      // 如果有电话号码，添加到注册数据
      if (data.phone) {
        registerData.phone = data.phone
      }
      
      // 调用注册接口
      const response = await axios.post(`${API_URL}/users/register/`, registerData)
      console.log('注册响应:', response.data)
      
      // 如果注册成功，自动登录
      if (response.data && response.data.id) {
        try {
          // 自动登录
          const loginResponse = await login({
            username: data.username,
            password: data.password
          })
          
          console.log('注册后自动登录成功:', loginResponse)
          
          // 设置默认头像 - 确保一定会设置头像
          console.log('注册用户设置默认头像')
          setTimeout(async () => {
            try {
              await userApi.setDefaultAvatar()
              console.log('注册用户默认头像设置成功')
              
              // 重新加载用户信息以显示头像
              await loadUser()
            } catch (avatarError) {
              console.error('注册用户设置默认头像失败:', avatarError)
            }
          }, 1000) // 延迟1秒执行，确保登录完全处理完毕
          
          return loginResponse
        } catch (loginError) {
          console.error('注册成功但自动登录失败:', loginError)
          error.value = '注册成功，请手动登录'
          return response.data
        }
      }

      return response.data
    } catch (err: any) {
      console.error('注册失败:', err)
      error.value = err.response?.data?.detail || 
                  err.response?.data?.message || 
                  '注册失败，请检查输入信息'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 登出
  const logout = () => {
    clearAuth()
    router.push('/login')
  }

  // 刷新token
  const refreshAccessToken = async () => {
    if (!refreshToken.value) {
      throw new Error('No refresh token')
    }
    try {
      const response = await axios.post(`${API_URL}/users/token/refresh/`, {
        refresh: refreshToken.value
      })
      token.value = response.data.access
      localStorage.setItem('token', response.data.access)
      axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.access}`
      return response.data
    } catch (error) {
      clearAuth()
      router.push('/login')
      throw error
    }
  }

  // 初始化axios拦截器
  axios.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config
      if (error.response?.status === 401 && !originalRequest._retry && refreshToken.value) {
        originalRequest._retry = true
        try {
          // 尝试刷新token
          await refreshAccessToken()
          // 重新发送之前失败的请求
          return axios(originalRequest)
        } catch (refreshError) {
          // 刷新token失败，登出
          console.error('刷新token失败:', refreshError)
          clearAuth()
          router.push('/login')
          return Promise.reject(refreshError)
        }
      }
      return Promise.reject(error)
    }
  )

  return {
    user,
    token,
    refreshToken,
    profile,
    loading,
    error,
    isAuthenticated,
    login,
    register,
    logout,
    loadUser,
    initializeAuth,
    refreshAccessToken
  }
}) 
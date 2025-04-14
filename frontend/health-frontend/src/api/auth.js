import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  headers: {
    'Content-Type': 'application/json'
  }
})

// 添加请求拦截器
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('health_app_token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 添加响应拦截器
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('health_app_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authApi = {
  // 登录接口
  login: async (username, password) => {
    try {
      console.log('调用登录API')
      const response = await api.post('/api/users/login/', {
        username,
        password
      })
      console.log('登录API返回:', response)
      return response.data
    } catch (error) {
      console.error('登录API错误:', error)
      throw error
    }
  },

  // 注册接口
  register: async (userData) => {
    try {
      console.log('调用注册API')
      const response = await api.post('/api/users/register/', userData)
      console.log('注册API返回:', response)
      return response.data
    } catch (error) {
      console.error('注册API错误:', error)
      throw error
    }
  },

  // 刷新令牌
  refreshToken: async (refreshToken) => {
    try {
      const response = await api.post('/api/users/token/refresh/', {
        refresh: refreshToken
      })
      return response.data
    } catch (error) {
      console.error('刷新令牌错误:', error)
      throw error
    }
  }
}

// 为了向后兼容，导出单独的函数
export const login = authApi.login
export const register = authApi.register
export const refreshToken = authApi.refreshToken 
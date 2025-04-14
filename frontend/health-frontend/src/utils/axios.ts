import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例
const instance = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
instance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
instance.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    if (error.response) {
      const { status } = error.response
      if (status === 401) {
        // Token过期，尝试刷新
        const refreshToken = localStorage.getItem('refreshToken')
        if (refreshToken) {
          try {
            const response = await instance.post('/api/users/token/refresh/', {
              refresh: refreshToken
            })
            const newToken = response.data.access
            localStorage.setItem('token', newToken)
            error.config.headers.Authorization = `Bearer ${newToken}`
            return instance(error.config)
          } catch (refreshError) {
            // 刷新token失败，清除用户信息并跳转到登录页
            localStorage.removeItem('token')
            localStorage.removeItem('refreshToken')
            window.location.href = '/login'
            return Promise.reject(refreshError)
          }
        }
      }
      // 显示错误信息
      const errorMessage = error.response.data?.detail || error.response.data?.message || '请求失败，请稍后重试'
      ElMessage.error(errorMessage)
    }
    return Promise.reject(error)
  }
)

export default instance 
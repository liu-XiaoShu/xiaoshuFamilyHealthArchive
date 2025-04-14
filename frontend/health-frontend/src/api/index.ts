import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

// 创建axios实例
const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    if (error.response?.status === 401) {
      const authStore = useAuthStore()
      try {
        await authStore.refreshAccessToken()
        const originalRequest = error.config
        originalRequest.headers.Authorization = `Bearer ${authStore.token}`
        return api(originalRequest)
      } catch (refreshError) {
        authStore.clearAuth()
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }
    return Promise.reject(error)
  }
)

// 健康检查API
export const healthCheck = () => {
  return axios.get(`${API_URL}/health/`)
    .then(response => {
      return {
        status: 'healthy',
        message: response.data.message
      }
    })
    .catch(error => {
      console.error('健康检查失败:', error)
      return {
        status: 'unhealthy',
        message: '后端服务不可用，请检查服务器状态'
      }
    })
}

// 用户相关接口
export const auth = {
  login: (data: { username: string; password: string }) =>
    api.post('/users/login/', data),
  register: (data: { username: string; email: string; password: string }) =>
    api.post('/users/register/', data),
  logout: () => api.post('/users/logout/'),
  getProfile: () => api.get('/users/me/')
}

// 健康记录相关接口
export const records = {
  getList: () => api.get('/records/'),
  getDetail: (id: number) => api.get(`/records/${id}/`),
  create: (data: any) => api.post('/records/', data),
  update: (id: number, data: any) => api.put(`/records/${id}/`, data),
  delete: (id: number) => api.delete(`/records/${id}/`)
}

export default api 
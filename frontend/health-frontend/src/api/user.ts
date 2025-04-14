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

export const userApi = {
  // 用户认证相关
  login: async (username: string, password: string) => {
    const response = await api.post('/users/login/', { username, password })
    return response.data
  },
  
  register: async (userData: any) => {
    const response = await api.post('/users/register/', userData)
    return response.data
  },
  
  refreshToken: async (refreshToken: string) => {
    const response = await api.post('/users/token/refresh/', { refresh: refreshToken })
    return response.data
  },
  
  // 用户资料相关
  getProfile: async () => {
    const response = await api.get('/users/profile/')
    return response.data
  },
  
  updateProfile: async (profileData: any) => {
    const response = await api.put('/users/profile/', profileData)
    return response.data
  },
  
  // 头像相关
  updateAvatar: async (avatarFile: File) => {
    const formData = new FormData()
    formData.append('avatar', avatarFile)
    const response = await api.put('/users/avatar/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },
  
  // 默认头像相关
  getDefaultAvatarByAgeGender: async (age: number, gender: string) => {
    const response = await api.get(`/users/default-avatars/by-age-gender/?age=${age}&gender=${gender}`)
    return response.data
  },
  
  getAllDefaultAvatars: async () => {
    const response = await api.get('/users/default-avatars/')
    return response.data
  }
}

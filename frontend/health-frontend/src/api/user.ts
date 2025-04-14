import axios from 'axios'
import api from './index'  // 导入包含认证信息的axios实例

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

// 用户个人资料接口
export interface UserProfile {
  id?: number;
  username: string;
  email: string;
  phone?: string;
  nickname?: string;
  avatar?: string;
  birth_date?: string;
  gender?: string;
  height?: number;
  weight?: number;
  blood_type?: string;
  emergency_contact?: {
    name: string;
    relationship: string;
    phone: string;
  };
  allergies?: string[];
  notes?: string;
}

// 用户API
export const userApi = {
  // 获取用户资料
  getProfile: async () => {
    const response = await api.get('/users/me/')
    return response.data
  },

  // 更新用户资料
  updateProfile: async (data: Partial<UserProfile>) => {
    console.log('更新用户资料数据:', data)
    try {
      const response = await api.patch('/users/me/', data)
      console.log('用户资料更新成功:', response.data)
      return response.data
    } catch (error) {
      console.error('用户资料更新失败:', error)
      throw error
    }
  },

  // 上传头像
  updateAvatar: async (file: File) => {
    console.log('上传头像文件:', file.name, file.size, file.type)
    const formData = new FormData()
    formData.append('avatar', file)
    
    const response = await api.post('/users/avatar/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    console.log('头像上传响应:', response.data)
    return response.data
  },

  // 获取当前用户头像
  getAvatar: async () => {
    const response = await api.get('/users/avatar/')
    return response.data
  },
  
  // 获取默认头像
  getDefaultAvatar: async (category: string) => {
    const response = await api.get(`/users/default-avatars/by_category/?category=${category}`)
    return response.data
  },
  
  // 获取所有默认头像
  getAllDefaultAvatars: async () => {
    const response = await api.get('/users/default-avatars/')
    return response.data
  },
  
  // 设置默认头像（通过下载默认头像并上传）
  setDefaultAvatar: async () => {
    try {
      console.log('开始设置默认头像...')
      // 1. 获取所有默认头像
      const defaultAvatarsResponse = await api.get('/users/default-avatars/')
      console.log('获取默认头像列表成功:', defaultAvatarsResponse.data)
      
      if (!defaultAvatarsResponse.data || defaultAvatarsResponse.data.length === 0) {
        console.error('没有默认头像可用')
        throw new Error('没有默认头像可用')
      }
      
      // 2. 随机选择一个头像
      const randomIndex = Math.floor(Math.random() * defaultAvatarsResponse.data.length)
      const avatar = defaultAvatarsResponse.data[randomIndex]
      console.log('选择的默认头像:', avatar)
      
      if (!avatar.image) {
        console.error('所选默认头像没有图片URL')
        throw new Error('所选默认头像没有图片URL')
      }
      
      // 3. 获取完整的图片URL（使用直接URL）
      const imageUrl = avatar.image
      console.log('头像图片URL:', imageUrl)
        
      // 4. 下载头像图片
      const imageResponse = await axios.get(imageUrl, { responseType: 'blob' })
      console.log('头像图片下载成功, 内容类型:', imageResponse.headers['content-type'])
      
      // 5. 创建文件对象
      const contentType = imageResponse.headers['content-type'] || 'image/png'
      const extension = contentType.split('/')[1] || 'png'
      const filename = `default-avatar-${Date.now()}.${extension}`
      
      const file = new File([imageResponse.data], filename, { type: contentType })
      console.log('创建文件对象成功:', filename, file.size, 'bytes')
      
      // 6. 上传头像
      const formData = new FormData()
      formData.append('avatar', file)
      console.log('开始上传默认头像...')
      
      const uploadResponse = await api.post('/users/avatar/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      
      console.log('默认头像上传成功:', uploadResponse.data)
      return uploadResponse.data
    } catch (error) {
      console.error('设置默认头像失败:', error)
      throw error
    }
  },

  // 更新密码
  updatePassword: async (data: { current_password: string; new_password: string }) => {
    const response = await api.post('/users/change-password/', data)
    return response.data
  },

  // 健康信息相关
  updateHealthInfo: async (data: {
    height?: number;
    weight?: number;
    blood_type?: string;
    allergies?: string[];
  }) => {
    console.log('更新健康信息:', data)
    try {
      // 确保传递的健康信息数据格式正确
      const formattedData = {
        ...data,
        allergies: Array.isArray(data.allergies) ? data.allergies.join(',') : data.allergies
      }
      const response = await api.post('/users/health-info/', formattedData)
      console.log('健康信息更新成功:', response.data)
      return response.data
    } catch (error) {
      console.error('健康信息更新失败:', error)
      throw error
    }
  },

  // 获取健康信息
  getHealthInfo: async () => {
    const response = await api.get('/users/health-info/')
    return response.data
  }
} 
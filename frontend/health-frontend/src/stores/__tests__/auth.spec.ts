import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '../auth'
import axios from 'axios'

// 模拟axios
vi.mock('axios')

// 模拟路由
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: vi.fn()
  })
}))

describe('Auth Store', () => {
  // 在每个测试前初始化Pinia
  beforeEach(() => {
    // 创建一个新的Pinia实例
    setActivePinia(createPinia())
    
    // 重置localStorage模拟
    vi.spyOn(Storage.prototype, 'getItem').mockImplementation((key: string) => {
      return null
    })
    vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {})
    vi.spyOn(Storage.prototype, 'removeItem').mockImplementation(() => {})
    
    // 重置axios模拟
    vi.mocked(axios.post).mockReset()
    vi.mocked(axios.get).mockReset()
    vi.mocked(axios.defaults.headers.common).mockReset()
  })
  
  describe('初始状态', () => {
    it('应该有正确的初始状态', () => {
      const store = useAuthStore()
      expect(store.user).toBeNull()
      expect(store.token).toBeNull()
      expect(store.refreshToken).toBeNull()
      expect(store.loading).toBe(false)
      expect(store.error).toBeNull()
      expect(store.isAuthenticated).toBe(false)
    })
  })
  
  describe('setAuth', () => {
    it('应该正确设置认证信息', () => {
      const store = useAuthStore()
      const user = { id: 1, username: 'test', email: 'test@example.com', phone: '13800138000' }
      const token = 'test-token'
      const refreshToken = 'test-refresh-token'
      
      store.setAuth(user, token, refreshToken)
      
      expect(store.user).toEqual(user)
      expect(store.token).toBe(token)
      expect(store.refreshToken).toBe(refreshToken)
      expect(store.isAuthenticated).toBe(true)
      expect(localStorage.setItem).toHaveBeenCalledWith('token', token)
      expect(localStorage.setItem).toHaveBeenCalledWith('refreshToken', refreshToken)
      expect(localStorage.setItem).toHaveBeenCalledWith('user', JSON.stringify(user))
    })
  })
  
  describe('clearAuth', () => {
    it('应该正确清除认证信息', () => {
      const store = useAuthStore()
      const user = { id: 1, username: 'test', email: 'test@example.com', phone: '13800138000' }
      const token = 'test-token'
      const refreshToken = 'test-refresh-token'
      
      // 先设置认证信息
      store.setAuth(user, token, refreshToken)
      
      // 然后清除
      store.clearAuth()
      
      expect(store.user).toBeNull()
      expect(store.token).toBeNull()
      expect(store.refreshToken).toBeNull()
      expect(store.isAuthenticated).toBe(false)
      expect(localStorage.removeItem).toHaveBeenCalledWith('token')
      expect(localStorage.removeItem).toHaveBeenCalledWith('refreshToken')
      expect(localStorage.removeItem).toHaveBeenCalledWith('user')
    })
  })
  
  describe('login', () => {
    it('登录成功时应该设置认证信息', async () => {
      const loginData = { username: 'test', password: 'password' }
      const responseData = {
        access: 'access-token',
        refresh: 'refresh-token',
        user: { id: 1, username: 'test', email: 'test@example.com', phone: '13800138000' }
      }
      
      // 模拟axios.post返回值
      vi.mocked(axios.post).mockResolvedValue({ data: responseData })
      
      const store = useAuthStore()
      await store.login(loginData)
      
      expect(axios.post).toHaveBeenCalledWith(expect.stringContaining('/users/login/'), loginData)
      expect(store.user).toEqual(responseData.user)
      expect(store.token).toBe(responseData.access)
      expect(store.refreshToken).toBe(responseData.refresh)
      expect(store.isAuthenticated).toBe(true)
      expect(store.loading).toBe(false)
      expect(store.error).toBeNull()
    })
    
    it('登录失败时应该设置错误信息', async () => {
      const loginData = { username: 'test', password: 'wrong-password' }
      const errorResponse = {
        response: {
          data: {
            detail: '用户名或密码不正确'
          }
        }
      }
      
      // 模拟axios.post抛出错误
      vi.mocked(axios.post).mockRejectedValue(errorResponse)
      
      const store = useAuthStore()
      
      await expect(store.login(loginData)).rejects.toEqual(errorResponse)
      
      expect(store.user).toBeNull()
      expect(store.token).toBeNull()
      expect(store.refreshToken).toBeNull()
      expect(store.isAuthenticated).toBe(false)
      expect(store.loading).toBe(false)
      expect(store.error).toBe('用户名或密码不正确')
    })
  })
  
  describe('initializeAuth', () => {
    it('应该从localStorage初始化认证状态', async () => {
      const user = { id: 1, username: 'test', email: 'test@example.com', phone: '13800138000' }
      const token = 'stored-token'
      const userStr = JSON.stringify(user)
      
      // 模拟localStorage返回值
      vi.spyOn(Storage.prototype, 'getItem').mockImplementation((key: string) => {
        if (key === 'token') return token
        if (key === 'user') return userStr
        return null
      })
      
      // 模拟loadUser成功
      vi.mocked(axios.get).mockResolvedValue({ data: user })
      
      const store = useAuthStore()
      await store.initializeAuth()
      
      expect(store.token).toBe(token)
      expect(store.user).toEqual(user)
      expect(store.isAuthenticated).toBe(true)
      expect(axios.get).toHaveBeenCalled()
    })
  })
}) 
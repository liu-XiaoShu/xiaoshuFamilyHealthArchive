import { describe, it, expect, vi, beforeEach } from 'vitest'
import axios from 'axios'
import { healthCheck, auth, records } from '../index'

// 模拟axios
vi.mock('axios')

// 模拟store
vi.mock('@/stores/auth', () => ({
  useAuthStore: () => ({
    token: 'test-token',
    refreshToken: 'test-refresh-token',
    refreshAccessToken: vi.fn(),
    clearAuth: vi.fn()
  })
}))

describe('API', () => {
  beforeEach(() => {
    // 重置模拟
    vi.mocked(axios.get).mockReset()
    vi.mocked(axios.post).mockReset()
    vi.mocked(axios.put).mockReset()
    vi.mocked(axios.delete).mockReset()
  })
  
  describe('healthCheck', () => {
    it('健康检查成功时应返回健康状态', async () => {
      // 模拟axios.get返回值
      vi.mocked(axios.get).mockResolvedValue({
        data: {
          status: 'healthy',
          message: '后端服务正常运行'
        }
      })
      
      const result = await healthCheck()
      
      expect(axios.get).toHaveBeenCalledWith(expect.stringContaining('/health/'))
      expect(result.status).toBe('healthy')
      expect(result.message).toBe('后端服务正常运行')
    })
    
    it('健康检查失败时应返回不健康状态', async () => {
      // 模拟axios.get抛出错误
      vi.mocked(axios.get).mockRejectedValue(new Error('连接失败'))
      
      const result = await healthCheck()
      
      expect(axios.get).toHaveBeenCalledWith(expect.stringContaining('/health/'))
      expect(result.status).toBe('unhealthy')
      expect(result.message).toBe('后端服务不可用，请检查服务器状态')
    })
  })
  
  describe('auth API', () => {
    it('login应发送正确的请求', async () => {
      const loginData = { username: 'test', password: 'password' }
      const mockResponse = { data: { token: 'test-token' } }
      
      // 使用自定义的axios实例，需要模拟post方法
      vi.spyOn(axios, 'create').mockReturnValue({
        post: vi.fn().mockResolvedValue(mockResponse),
        get: vi.fn(),
        put: vi.fn(),
        delete: vi.fn(),
        interceptors: {
          request: { use: vi.fn() },
          response: { use: vi.fn() }
        }
      } as any)
      
      await auth.login(loginData)
      
      // TODO: 因为使用axios.create创建的实例，无法直接检查是否调用，
      // 实际测试需要更复杂的模拟设置
    })
  })
  
  describe('records API', () => {
    it('getList应发送正确的请求', async () => {
      // 使用自定义的axios实例，需要模拟
      vi.spyOn(axios, 'create').mockReturnValue({
        get: vi.fn().mockResolvedValue({ data: [] }),
        post: vi.fn(),
        put: vi.fn(),
        delete: vi.fn(),
        interceptors: {
          request: { use: vi.fn() },
          response: { use: vi.fn() }
        }
      } as any)
      
      await records.getList()
      
      // TODO: 同上，因为使用axios.create创建的实例，
      // 实际测试需要更复杂的模拟设置
    })
  })
}) 
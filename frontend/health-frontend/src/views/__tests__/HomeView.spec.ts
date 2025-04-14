import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import ElementPlus from 'element-plus'
import HomeView from '../HomeView.vue'
import { recordsApi } from '@/api/records'
import { useAuthStore } from '@/stores/auth'

// Mock API调用
vi.mock('@/api/records', () => ({
  recordsApi: {
    getHealthStatistics: vi.fn().mockResolvedValue({
      data: {
        medical_records: { total: 5 },
        medication_records: { total: 3 },
        vaccination_records: { total: 2 },
        physical_exams: { total: 1 }
      }
    }),
    getHealthTrends: vi.fn().mockResolvedValue({
      data: {
        dates: ['2024-03-01', '2024-03-02', '2024-03-03'],
        bloodPressure: {
          systolic: [120, 118, 122],
          diastolic: [80, 78, 82]
        },
        bloodSugar: [5.6, 5.8, 5.7],
        weight: [70, 70.5, 70.2]
      }
    }),
    getRecentActivities: vi.fn().mockResolvedValue({
      data: [
        {
          id: 1,
          type: 'medical',
          description: '普通感冒就医',
          date: '2024-03-01'
        }
      ]
    })
  }
}))

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: HomeView
    }
  ]
})

describe('HomeView', () => {
  beforeEach(() => {
    // 创建并激活Pinia实例
    setActivePinia(createPinia())
    
    // 设置认证状态
    const authStore = useAuthStore()
    authStore.setAuth(
      {
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        phone: '13800138000'
      },
      'fake-token',
      'fake-refresh-token'
    )
  })

  it('加载并显示健康统计数据', async () => {
    const wrapper = mount(HomeView, {
      global: {
        plugins: [ElementPlus, router]
      }
    })

    // 等待异步操作完成
    await new Promise(resolve => setTimeout(resolve, 500))

    // 验证API调用
    expect(recordsApi.getHealthStatistics).toHaveBeenCalled()
    expect(recordsApi.getHealthTrends).toHaveBeenCalled()
    expect(recordsApi.getRecentActivities).toHaveBeenCalled()

    // 验证统计数据显示
    const stats = wrapper.findAll('.stat-value')
    expect(stats[0].text()).toBe('5') // 就医记录
    expect(stats[1].text()).toBe('3') // 用药记录
    expect(stats[2].text()).toBe('2') // 疫苗记录
    expect(stats[3].text()).toBe('1') // 体检报告
  })

  it('显示健康趋势图表', async () => {
    const wrapper = mount(HomeView, {
      global: {
        plugins: [ElementPlus, router]
      }
    })

    await new Promise(resolve => setTimeout(resolve, 500))

    // 验证图表组件存在
    expect(wrapper.findComponent({ name: 'LineChart' }).exists()).toBe(true)
  })

  it('导航到记录详情页面', async () => {
    const wrapper = mount(HomeView, {
      global: {
        plugins: [ElementPlus, router]
      }
    })

    // 模拟点击就医记录卡片
    await wrapper.find('.feature-card').trigger('click')
    
    // 验证路由导航
    expect(router.currentRoute.value.path).toBe('/medical-records')
  })

  it('打开添加记录对话框', async () => {
    const wrapper = mount(HomeView, {
      global: {
        plugins: [ElementPlus, router]
      }
    })

    // 点击添加按钮
    const addButton = wrapper.find('.el-button--success')
    await addButton.trigger('click')

    // 验证对话框显示
    expect(wrapper.find('.el-dialog').exists()).toBe(true)
  })
}) 
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import ElementPlus from 'element-plus'
import BodyModel from '../BodyModel.vue'
import { recordsApi } from '@/api/records'

// Mock recordsApi
vi.mock('@/api/records', () => ({
  recordsApi: {
    getAbnormalOrgans: vi.fn().mockResolvedValue([
      { 
        id: 1, 
        name: '心脏', 
        status: 'warning', 
        description: '心率偏快',
        relatedRecords: [
          { id: 1, type: 'physical', date: '2024-03-01' }
        ]
      },
      { 
        id: 2, 
        name: '肝脏', 
        status: 'danger', 
        description: '肝功能异常',
        relatedRecords: [
          { id: 2, type: 'medical', date: '2024-03-02' }
        ]
      }
    ])
  }
}))

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: { template: '<div>Home</div>' }
    },
    {
      path: '/physical-exams/:id',
      name: 'physical-exam-detail',
      component: { template: '<div>Physical Exam Detail</div>' }
    },
    {
      path: '/medical-records/:id',
      name: 'medical-record-detail',
      component: { template: '<div>Medical Record Detail</div>' }
    }
  ]
})

describe('BodyModel', () => {
  it('正确渲染人体模型', async () => {
    const wrapper = mount(BodyModel, {
      global: {
        plugins: [ElementPlus, router]
      }
    })
    
    expect(wrapper.find('.body-model-container').exists()).toBe(true)
    expect(wrapper.find('svg').exists()).toBe(true)
  })

  it('加载并显示异常器官标记', async () => {
    const wrapper = mount(BodyModel, {
      global: {
        plugins: [ElementPlus, router]
      }
    })
    
    // 等待异步操作完成
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 验证API调用
    expect(recordsApi.getAbnormalOrgans).toHaveBeenCalled()
    
    // 验证标记渲染
    const markers = wrapper.findAll('.organ-marker')
    expect(markers.length).toBe(2)
    
    // 验证标记状态类
    expect(markers[0].classes()).toContain('status-warning')
    expect(markers[1].classes()).toContain('status-danger')
  })

  it('点击标记显示器官详情', async () => {
    const wrapper = mount(BodyModel, {
      global: {
        plugins: [ElementPlus, router]
      }
    })
    
    // 等待数据加载
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 点击第一个标记
    const markers = wrapper.findAll('.organ-marker')
    await markers[0].trigger('click')
    
    // 验证详情对话框显示
    const dialog = wrapper.find('.organ-details-dialog')
    expect(dialog.exists()).toBe(true)
    expect(dialog.text()).toContain('心脏')
    expect(dialog.text()).toContain('心率偏快')
  })

  it('点击相关记录导航到详情页面', async () => {
    const wrapper = mount(BodyModel, {
      global: {
        plugins: [ElementPlus, router]
      }
    })
    
    // 等待数据加载
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 点击标记显示详情
    const markers = wrapper.findAll('.organ-marker')
    await markers[0].trigger('click')
    
    // 点击相关记录链接
    const recordLink = wrapper.find('.record-link')
    await recordLink.trigger('click')
    
    // 验证路由导航
    expect(router.currentRoute.value.name).toBe('physical-exam-detail')
    expect(router.currentRoute.value.params.id).toBe('1')
  })

  it('正确处理加载状态', async () => {
    const wrapper = mount(BodyModel, {
      global: {
        plugins: [ElementPlus, router]
      }
    })
    
    // 验证初始加载状态
    expect(wrapper.find('.loading-overlay').exists()).toBe(true)
    
    // 等待数据加载完成
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 验证加载状态消失
    expect(wrapper.find('.loading-overlay').exists()).toBe(false)
  })
}) 
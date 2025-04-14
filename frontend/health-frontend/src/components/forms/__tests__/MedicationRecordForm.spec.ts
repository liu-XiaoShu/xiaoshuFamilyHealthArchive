import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ElementPlus from 'element-plus'
import MedicationRecordForm from '../MedicationRecordForm.vue'
import { ElMessage } from 'element-plus'

vi.mock('element-plus', async () => {
  const actual = await vi.importActual('element-plus')
  return {
    ...actual,
    ElMessage: {
      error: vi.fn()
    }
  }
})

describe('MedicationRecordForm', () => {
  const mountForm = () => {
    return mount(MedicationRecordForm, {
      global: {
        plugins: [ElementPlus]
      }
    })
  }

  it('正确渲染表单字段', () => {
    const wrapper = mountForm()
    
    // 验证必填字段存在
    expect(wrapper.find('[data-test="medication-name"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="dosage"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="frequency"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="start-date"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="end-date"]').exists()).toBe(true)
  })

  it('提交前验证必填字段', async () => {
    const wrapper = mountForm()
    
    // 尝试提交空表单
    await wrapper.find('button[type="submit"]').trigger('click')
    
    // 验证错误提示
    expect(ElMessage.error).toHaveBeenCalledWith('请完成必填项')
  })

  it('验证结束日期不能早于开始日期', async () => {
    const wrapper = mountForm()
    
    // 设置开始日期和结束日期
    await wrapper.find('[data-test="start-date"]').setValue('2024-03-20')
    await wrapper.find('[data-test="end-date"]').setValue('2024-03-19')
    
    // 尝试提交表单
    await wrapper.find('button[type="submit"]').trigger('click')
    
    // 验证错误提示
    expect(ElMessage.error).toHaveBeenCalledWith('结束日期不能早于开始日期')
  })

  it('正确处理副作用的添加和删除', async () => {
    const wrapper = mountForm()
    
    // 添加副作用
    const input = wrapper.find('[data-test="side-effect-input"]')
    await input.setValue('头晕')
    await input.trigger('keyup.enter')
    
    // 验证副作用标签是否添加
    const tags = wrapper.findAll('.side-effect-tag')
    expect(tags.length).toBe(1)
    expect(tags[0].text()).toContain('头晕')
    
    // 删除副作用标签
    await tags[0].find('.el-tag__close').trigger('click')
    
    // 验证标签是否被删除
    expect(wrapper.findAll('.side-effect-tag').length).toBe(0)
  })

  it('成功提交表单时触发submit事件', async () => {
    const wrapper = mountForm()
    
    // 填写必填字段
    await wrapper.find('[data-test="medication-name"]').setValue('布洛芬')
    await wrapper.find('[data-test="dosage"]').setValue('200mg')
    await wrapper.find('[data-test="frequency"]').setValue('每日三次')
    await wrapper.find('[data-test="start-date"]').setValue('2024-03-20')
    await wrapper.find('[data-test="end-date"]').setValue('2024-03-25')
    
    // 提交表单
    await wrapper.find('button[type="submit"]').trigger('click')
    
    // 验证emit事件
    expect(wrapper.emitted().submit).toBeTruthy()
    expect(wrapper.emitted().submit[0][0]).toMatchObject({
      medicationName: '布洛芬',
      dosage: '200mg',
      frequency: '每日三次',
      startDate: '2024-03-20',
      endDate: '2024-03-25'
    })
  })

  it('点击取消按钮时触发cancel事件', async () => {
    const wrapper = mountForm()
    
    await wrapper.find('button[type="button"]').trigger('click')
    
    expect(wrapper.emitted().cancel).toBeTruthy()
  })
}) 
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ElementPlus from 'element-plus'
import VaccinationRecordForm from '../VaccinationRecordForm.vue'
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

describe('VaccinationRecordForm', () => {
  const mountForm = () => {
    return mount(VaccinationRecordForm, {
      global: {
        plugins: [ElementPlus]
      }
    })
  }

  it('正确渲染表单字段', () => {
    const wrapper = mountForm()
    
    // 验证必填字段存在
    expect(wrapper.find('[data-test="vaccine-name"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="vaccination-date"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="manufacturer"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="batch-number"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="vaccination-site"]').exists()).toBe(true)
  })

  it('提交前验证必填字段', async () => {
    const wrapper = mountForm()
    
    // 尝试提交空表单
    await wrapper.find('button[type="submit"]').trigger('click')
    
    // 验证错误提示
    expect(ElMessage.error).toHaveBeenCalledWith('请完成必填项')
  })

  it('正确处理不良反应的添加和删除', async () => {
    const wrapper = mountForm()
    
    // 添加不良反应
    const input = wrapper.find('[data-test="reaction-input"]')
    await input.setValue('发烧')
    await input.trigger('keyup.enter')
    
    // 验证不良反应标签是否添加
    const tags = wrapper.findAll('.reaction-tag')
    expect(tags.length).toBe(1)
    expect(tags[0].text()).toContain('发烧')
    
    // 删除不良反应标签
    await tags[0].find('.el-tag__close').trigger('click')
    
    // 验证标签是否被删除
    expect(wrapper.findAll('.reaction-tag').length).toBe(0)
  })

  it('验证下次接种日期必须晚于接种日期', async () => {
    const wrapper = mountForm()
    
    // 设置接种日期和下次接种日期
    await wrapper.find('[data-test="vaccination-date"]').setValue('2024-03-20')
    await wrapper.find('[data-test="next-dose-date"]').setValue('2024-03-19')
    
    // 尝试提交表单
    await wrapper.find('button[type="submit"]').trigger('click')
    
    // 验证错误提示
    expect(ElMessage.error).toHaveBeenCalledWith('下次接种日期必须晚于接种日期')
  })

  it('成功提交表单时触发submit事件', async () => {
    const wrapper = mountForm()
    
    // 填写必填字段
    await wrapper.find('[data-test="vaccine-name"]').setValue('新冠疫苗')
    await wrapper.find('[data-test="vaccination-date"]').setValue('2024-03-20')
    await wrapper.find('[data-test="manufacturer"]').setValue('科兴生物')
    await wrapper.find('[data-test="batch-number"]').setValue('20240320001')
    await wrapper.find('[data-test="vaccination-site"]').setValue('左臂')
    
    // 提交表单
    await wrapper.find('button[type="submit"]').trigger('click')
    
    // 验证emit事件
    expect(wrapper.emitted().submit).toBeTruthy()
    const submitData = wrapper.emitted().submit[0][0] as Record<string, string>
    expect(submitData).toMatchObject({
      vaccineName: '新冠疫苗',
      vaccinationDate: '2024-03-20',
      manufacturer: '科兴生物',
      batchNumber: '20240320001',
      vaccinationSite: '左臂'
    })
  })

  it('点击取消按钮时触发cancel事件', async () => {
    const wrapper = mountForm()
    
    await wrapper.find('button[type="button"]').trigger('click')
    
    expect(wrapper.emitted().cancel).toBeTruthy()
  })
}) 
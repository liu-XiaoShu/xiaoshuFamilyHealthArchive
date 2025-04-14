import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ElementPlus from 'element-plus'
import PhysicalExamForm from '../PhysicalExamForm.vue'
import { ElMessage } from 'element-plus'
import type { PhysicalExamFormData } from '@/types/records'

vi.mock('element-plus', async () => {
  const actual = await vi.importActual('element-plus')
  return {
    ...actual,
    ElMessage: {
      error: vi.fn()
    }
  }
})

describe('PhysicalExamForm', () => {
  const mountForm = () => {
    return mount(PhysicalExamForm, {
      global: {
        plugins: [ElementPlus]
      }
    })
  }

  it('正确渲染表单字段', () => {
    const wrapper = mountForm()
    
    // 验证必填字段存在
    expect(wrapper.find('[data-test="exam-date"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="hospital"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="height"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="weight"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="blood-pressure"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="heart-rate"]').exists()).toBe(true)
  })

  it('提交前验证必填字段', async () => {
    const wrapper = mountForm()
    
    // 尝试提交空表单
    await wrapper.find('button[type="submit"]').trigger('click')
    
    // 验证错误提示
    expect(ElMessage.error).toHaveBeenCalledWith('请完成必填项')
  })

  it('验证身高和体重的输入范围', async () => {
    const wrapper = mountForm()
    
    // 输入无效的身高和体重
    await wrapper.find('[data-test="height"]').setValue('300')
    await wrapper.find('[data-test="weight"]').setValue('0')
    
    // 尝试提交表单
    await wrapper.find('button[type="submit"]').trigger('click')
    
    // 验证错误提示
    expect(ElMessage.error).toHaveBeenCalledWith('请输入有效的身高和体重')
  })

  it('正确处理异常项目的添加和删除', async () => {
    const wrapper = mountForm()
    
    // 添加异常项目
    const input = wrapper.find('[data-test="abnormal-item-input"]')
    await input.setValue('血压偏高')
    await input.trigger('keyup.enter')
    
    // 验证异常项目标签是否添加
    const tags = wrapper.findAll('.abnormal-item-tag')
    expect(tags.length).toBe(1)
    expect(tags[0].text()).toContain('血压偏高')
    
    // 删除异常项目标签
    await tags[0].find('.el-tag__close').trigger('click')
    
    // 验证标签是否被删除
    expect(wrapper.findAll('.abnormal-item-tag').length).toBe(0)
  })

  it('成功提交表单时触发submit事件', async () => {
    const wrapper = mountForm()
    
    // 填写必填字段
    await wrapper.find('[data-test="exam-date"]').setValue('2024-03-20')
    await wrapper.find('[data-test="hospital"]').setValue('协和医院')
    await wrapper.find('[data-test="height"]').setValue('170')
    await wrapper.find('[data-test="weight"]').setValue('65')
    await wrapper.find('[data-test="blood-pressure"]').setValue('120/80')
    await wrapper.find('[data-test="heart-rate"]').setValue('75')
    
    // 提交表单
    await wrapper.find('button[type="submit"]').trigger('click')
    
    // 验证emit事件
    expect(wrapper.emitted().submit).toBeTruthy()
    const submitData = wrapper.emitted().submit[0][0] as PhysicalExamFormData
    expect(submitData).toMatchObject({
      examDate: '2024-03-20',
      hospital: '协和医院',
      height: 170,
      weight: 65,
      bloodPressure: '120/80',
      heartRate: 75
    })
  })

  it('点击取消按钮时触发cancel事件', async () => {
    const wrapper = mountForm()
    
    await wrapper.find('button[type="button"]').trigger('click')
    
    expect(wrapper.emitted().cancel).toBeTruthy()
  })

  it('正确计算BMI值', async () => {
    const wrapper = mountForm()
    
    // 输入身高和体重
    await wrapper.find('[data-test="height"]').setValue('170')
    await wrapper.find('[data-test="weight"]').setValue('65')
    
    // 验证BMI计算结果
    const bmi = wrapper.find('[data-test="bmi-value"]')
    expect(bmi.text()).toContain('22.49') // BMI = 65 / (1.7 * 1.7)
  })

  it('正确处理文件上传', async () => {
    const wrapper = mountForm()
    
    // 模拟文件上传
    const file = new File([''], 'report.pdf', { type: 'application/pdf' })
    const input = wrapper.find('input[type="file"]')
    await input.trigger('change', { target: { files: [file] } })
    
    // 验证文件列表
    const fileList = wrapper.findAll('.uploaded-file')
    expect(fileList.length).toBe(1)
    expect(fileList[0].text()).toContain('report.pdf')
  })
}) 
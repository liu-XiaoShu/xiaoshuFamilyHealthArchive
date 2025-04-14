import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ElementPlus from 'element-plus'
import MedicalRecordForm from '../MedicalRecordForm.vue'
import { ElMessage } from 'element-plus'

// Mock Element Plus的消息提示
vi.mock('element-plus', async () => {
  const actual = await vi.importActual('element-plus')
  return {
    ...actual,
    ElMessage: {
      error: vi.fn()
    }
  }
})

describe('MedicalRecordForm', () => {
  const mountForm = () => {
    return mount(MedicalRecordForm, {
      global: {
        plugins: [ElementPlus]
      }
    })
  }

  it('正确渲染表单字段', () => {
    const wrapper = mountForm()
    
    // 验证必填字段存在
    expect(wrapper.find('[data-test="visit-date"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="hospital"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="department"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="reason"]').exists()).toBe(true)
  })

  it('提交前验证必填字段', async () => {
    const wrapper = mountForm()
    
    // 尝试提交空表单
    await wrapper.find('button[type="submit"]').trigger('click')
    
    // 验证错误提示
    expect(ElMessage.error).toHaveBeenCalledWith('请完成必填项')
  })

  it('正确处理处方药物的添加和删除', async () => {
    const wrapper = mountForm()
    
    // 点击添加药物按钮
    await wrapper.find('.add-prescription-btn').trigger('click')
    
    // 输入药物名称
    const input = wrapper.find('.prescription-input')
    await input.setValue('阿莫西林')
    await input.trigger('keyup.enter')
    
    // 验证药物标签是否添加
    const tags = wrapper.findAll('.prescription-tag')
    expect(tags.length).toBe(1)
    expect(tags[0].text()).toContain('阿莫西林')
    
    // 删除药物标签
    await tags[0].find('.el-tag__close').trigger('click')
    
    // 验证标签是否被删除
    expect(wrapper.findAll('.prescription-tag').length).toBe(0)
  })

  it('正确处理文件上传', async () => {
    const wrapper = mountForm()
    
    // 模拟文件上传
    const file = new File([''], 'test.jpg', { type: 'image/jpeg' })
    const input = wrapper.find('input[type="file"]')
    await input.trigger('change', { target: { files: [file] } })
    
    // 验证文件列表
    expect(wrapper.vm.fileList.length).toBe(1)
    expect(wrapper.vm.fileList[0].name).toBe('test.jpg')
  })

  it('成功提交表单时触发submit事件', async () => {
    const wrapper = mountForm()
    
    // 填写必填字段
    await wrapper.find('[data-test="hospital"]').setValue('测试医院')
    await wrapper.find('[data-test="department"]').setValue('内科')
    await wrapper.find('[data-test="reason"]').setValue('发烧')
    
    // 提交表单
    await wrapper.find('button[type="submit"]').trigger('click')
    
    // 验证emit事件
    expect(wrapper.emitted().submit).toBeTruthy()
    expect(wrapper.emitted().submit[0][0]).toMatchObject({
      hospital: '测试医院',
      department: '内科',
      reason: '发烧'
    })
  })

  it('点击取消按钮时触发cancel事件', async () => {
    const wrapper = mountForm()
    
    await wrapper.find('button[type="button"]').trigger('click')
    
    expect(wrapper.emitted().cancel).toBeTruthy()
  })
}) 
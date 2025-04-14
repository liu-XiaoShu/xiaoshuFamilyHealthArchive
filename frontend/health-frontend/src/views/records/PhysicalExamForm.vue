<template>
  <div class="physical-exam-form">
    <div class="page-header">
      <div class="page-title">{{ isEdit ? '编辑体检记录' : '新建体检记录' }}</div>
    </div>

    <div class="app-card">
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        class="exam-form"
        v-loading="loading"
      >
        <!-- 基本信息 -->
        <div class="form-section">
          <h3>基本信息</h3>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="体检日期" prop="exam_date">
                <el-date-picker
                  v-model="form.exam_date"
                  type="date"
                  placeholder="选择日期"
                  :disabled-date="disableFutureDate"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="体检类型" prop="exam_type">
                <el-select v-model="form.exam_type" placeholder="请选择" style="width: 100%">
                  <el-option label="年度体检" value="annual" />
                  <el-option label="入职体检" value="employment" />
                  <el-option label="其他" value="other" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="体检医院" prop="hospital">
            <el-input v-model="form.hospital" placeholder="请输入体检医院名称" />
          </el-form-item>
        </div>

        <!-- 体检指标 -->
        <div class="form-section">
          <h3>体检指标</h3>
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="身高(cm)" prop="height">
                <el-input-number
                  v-model="form.height"
                  :min="0"
                  :max="300"
                  :precision="1"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="体重(kg)" prop="weight">
                <el-input-number
                  v-model="form.weight"
                  :min="0"
                  :max="500"
                  :precision="1"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="BMI">
                <el-input :value="calculateBMI" disabled />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="血压" prop="blood_pressure">
                <el-input
                  v-model="form.blood_pressure"
                  placeholder="例如: 120/80"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="血糖(mmol/L)" prop="blood_sugar">
                <el-input-number
                  v-model="form.blood_sugar"
                  :min="0"
                  :max="30"
                  :precision="1"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="心率(次/分)" prop="heart_rate">
                <el-input-number
                  v-model="form.heart_rate"
                  :min="0"
                  :max="300"
                  :precision="0"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <!-- 体检结果 -->
        <div class="form-section">
          <h3>体检结果</h3>
          <el-form-item label="体检总结" prop="summary">
            <el-input
              v-model="form.summary"
              type="textarea"
              :rows="4"
              placeholder="请输入体检总结"
            />
          </el-form-item>

          <el-form-item label="医生建议" prop="advice">
            <el-input
              v-model="form.advice"
              type="textarea"
              :rows="4"
              placeholder="请输入医生建议"
            />
          </el-form-item>

          <el-form-item label="状态" prop="status">
            <el-radio-group v-model="form.status">
              <el-radio label="normal">正常</el-radio>
              <el-radio label="abnormal">异常</el-radio>
              <el-radio label="pending">待复查</el-radio>
            </el-radio-group>
          </el-form-item>
        </div>

        <!-- 附件上传 -->
        <div class="form-section">
          <h3>附件</h3>
          <el-form-item label="体检报告" prop="attachments">
            <el-upload
              v-model:file-list="fileList"
              :action="uploadUrl"
              :headers="uploadHeaders"
              :before-upload="beforeUpload"
              :on-success="handleUploadSuccess"
              :on-error="handleUploadError"
              :on-remove="handleRemove"
              multiple
            >
              <el-button type="primary">
                <el-icon><Upload /></el-icon>
                上传文件
              </el-button>
              <template #tip>
                <div class="el-upload__tip">
                  支持PDF、JPG、PNG格式，单个文件不超过10MB
                </div>
              </template>
            </el-upload>
          </el-form-item>
        </div>

        <!-- 表单操作 -->
        <div class="form-actions">
          <el-button @click="handleCancel">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            保存
          </el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, FormInstance, UploadProps, UploadUserFile } from 'element-plus'
import { Upload } from '@element-plus/icons-vue'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const formRef = ref<FormInstance>()

const isEdit = computed(() => route.params.id !== undefined)
const loading = ref(false)
const submitting = ref(false)
const fileList = ref<UploadUserFile[]>([])

// 表单数据
const form = reactive({
  exam_date: '',
  exam_type: '',
  hospital: '',
  height: undefined,
  weight: undefined,
  blood_pressure: '',
  blood_sugar: undefined,
  heart_rate: undefined,
  summary: '',
  advice: '',
  status: 'normal',
  attachments: [] as { id: number; name: string; url: string }[]
})

// 表单验证规则
const rules = {
  exam_date: [{ required: true, message: '请选择体检日期', trigger: 'change' }],
  exam_type: [{ required: true, message: '请选择体检类型', trigger: 'change' }],
  hospital: [{ required: true, message: '请输入体检医院', trigger: 'blur' }],
  height: [{ required: true, message: '请输入身高', trigger: 'blur' }],
  weight: [{ required: true, message: '请输入体重', trigger: 'blur' }],
  blood_pressure: [
    { required: true, message: '请输入血压', trigger: 'blur' },
    {
      pattern: /^\d{2,3}\/\d{2,3}$/,
      message: '请输入正确的血压格式，如: 120/80',
      trigger: 'blur'
    }
  ],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }],
  summary: [{ required: true, message: '请输入体检总结', trigger: 'blur' }]
}

// 计算BMI
const calculateBMI = computed(() => {
  if (!form.height || !form.weight) return '-'
  const heightInMeters = form.height / 100
  const bmi = form.weight / (heightInMeters * heightInMeters)
  return bmi.toFixed(1)
})

// 禁用未来日期
const disableFutureDate = (date: Date) => {
  return date > new Date()
}

// 上传相关配置
const uploadUrl = '/api/upload'
const uploadHeaders = {
  // 如果需要认证token
  // Authorization: `Bearer ${localStorage.getItem('token')}`
}

const beforeUpload: UploadProps['beforeUpload'] = (file) => {
  const isValidType = ['application/pdf', 'image/jpeg', 'image/png'].includes(file.type)
  const isLt10M = file.size / 1024 / 1024 < 10

  if (!isValidType) {
    ElMessage.error('只能上传PDF/JPG/PNG格式的文件!')
    return false
  }
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过10MB!')
    return false
  }
  return true
}

const handleUploadSuccess: UploadProps['onSuccess'] = (response, uploadFile) => {
  form.attachments.push({
    id: response.id,
    name: uploadFile.name,
    url: response.url
  })
  ElMessage.success('上传成功')
}

const handleUploadError: UploadProps['onError'] = () => {
  ElMessage.error('上传失败')
}

const handleRemove: UploadProps['onRemove'] = (file) => {
  const index = form.attachments.findIndex(item => item.name === file.name)
  if (index !== -1) {
    form.attachments.splice(index, 1)
  }
}

// 获取记录详情
const fetchExamDetail = async (id: string) => {
  loading.value = true
  try {
    const response = await axios.get(`/api/records/physical/${id}`)
    Object.assign(form, response.data)
    // 设置文件列表
    if (response.data.attachments) {
      fileList.value = response.data.attachments.map((item: any) => ({
        name: item.name,
        url: item.url
      }))
    }
  } catch (error) {
    ElMessage.error('获取记录详情失败')
    console.error('获取记录详情失败:', error)
  } finally {
    loading.value = false
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const url = isEdit.value
          ? `/api/records/physical/${route.params.id}`
          : '/api/records/physical'
        const method = isEdit.value ? 'put' : 'post'
        
        await axios[method](url, form)
        ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
        router.push('/records/physical')
      } catch (error: any) {
        ElMessage.error(error.response?.data?.message || '操作失败')
        console.error('提交失败:', error)
      } finally {
        submitting.value = false
      }
    }
  })
}

// 取消
const handleCancel = () => {
  router.back()
}

// 页面加载时获取详情
onMounted(() => {
  if (isEdit.value && route.params.id) {
    fetchExamDetail(route.params.id as string)
  }
})
</script>

<style scoped>
.physical-exam-form {
  padding: 20px;
}

.form-section {
  margin-bottom: 30px;
}

.form-section h3 {
  margin-bottom: 20px;
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 10px;
}

.form-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 40px;
}

:deep(.el-upload-list) {
  margin-top: 10px;
}

@media screen and (max-width: 768px) {
  .physical-exam-form {
    padding: 10px;
  }

  :deep(.el-form-item__label) {
    float: none;
    display: block;
    text-align: left;
    margin-bottom: 8px;
  }

  :deep(.el-form-item__content) {
    margin-left: 0 !important;
  }
}
</style> 
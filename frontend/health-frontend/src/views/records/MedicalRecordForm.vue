<template>
  <div class="medical-record-form">
    <div class="page-header">
      <h2>{{ isEdit ? '编辑就医记录' : '新建就医记录' }}</h2>
      <el-button @click="router.back()">返回</el-button>
    </div>

    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
      class="record-form"
      v-loading="loading"
    >
      <el-card class="form-card">
        <template #header>
          <div class="card-header">
            <span>基本信息</span>
          </div>
        </template>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="就诊日期" prop="visitDate">
              <el-date-picker
                v-model="form.visitDate"
                type="date"
                placeholder="请选择就诊日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="医院" prop="hospital">
              <el-input v-model="form.hospital" placeholder="请输入医院名称" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="科室" prop="department">
              <el-select v-model="form.department" placeholder="请选择科室" style="width: 100%">
                <el-option
                  v-for="dept in departments"
                  :key="dept.value"
                  :label="dept.label"
                  :value="dept.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="医生" prop="doctor">
              <el-input v-model="form.doctor" placeholder="请输入医生姓名" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="主诉" prop="chiefComplaint">
          <el-input
            v-model="form.chiefComplaint"
            type="textarea"
            rows="3"
            placeholder="请描述主要症状和不适"
          />
        </el-form-item>
      </el-card>

      <el-card class="form-card">
        <template #header>
          <div class="card-header">
            <span>诊疗信息</span>
          </div>
        </template>

        <el-form-item label="诊断结果" prop="diagnosis">
          <el-input
            v-model="form.diagnosis"
            type="textarea"
            rows="3"
            placeholder="请输入诊断结果"
          />
        </el-form-item>

        <el-form-item label="处理方案" prop="treatment">
          <el-input
            v-model="form.treatment"
            type="textarea"
            rows="3"
            placeholder="请输入处理方案"
          />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="复诊日期" prop="followUpDate">
              <el-date-picker
                v-model="form.followUpDate"
                type="date"
                placeholder="请选择复诊日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="费用" prop="cost">
              <el-input-number
                v-model="form.cost"
                :min="0"
                :precision="2"
                :step="10"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="备注" prop="notes">
          <el-input
            v-model="form.notes"
            type="textarea"
            rows="3"
            placeholder="请输入备注信息"
          />
        </el-form-item>
      </el-card>

      <el-card class="form-card">
        <template #header>
          <div class="card-header">
            <span>附件</span>
          </div>
        </template>

        <el-upload
          class="attachment-upload"
          action="/api/upload"
          :on-success="handleUploadSuccess"
          :on-error="handleUploadError"
          :on-remove="handleRemove"
          :file-list="form.attachments"
          multiple
        >
          <el-button type="primary">
            <el-icon><Upload /></el-icon>上传附件
          </el-button>
          <template #tip>
            <div class="el-upload__tip">
              支持上传就医相关的图片、文档等文件
            </div>
          </template>
        </el-upload>
      </el-card>

      <div class="form-actions">
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          保存
        </el-button>
        <el-button @click="router.back()">取消</el-button>
      </div>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Upload } from '@element-plus/icons-vue'
import type { FormInstance, UploadFile } from 'element-plus'
import { recordsApi } from '@/api/records'

const router = useRouter()
const route = useRoute()
const formRef = ref<FormInstance>()
const loading = ref(false)
const submitting = ref(false)
const isEdit = ref(false)

// 表单数据
const form = ref({
  visitDate: '',
  hospital: '',
  department: '',
  doctor: '',
  chiefComplaint: '',
  diagnosis: '',
  treatment: '',
  followUpDate: '',
  cost: 0,
  notes: '',
  attachments: [] as UploadFile[]
})

// 表单验证规则
const rules = {
  visitDate: [{ required: true, message: '请选择就诊日期', trigger: 'change' }],
  hospital: [{ required: true, message: '请输入医院名称', trigger: 'blur' }],
  department: [{ required: true, message: '请选择科室', trigger: 'change' }],
  chiefComplaint: [{ required: true, message: '请输入主诉', trigger: 'blur' }],
  diagnosis: [{ required: true, message: '请输入诊断结果', trigger: 'blur' }],
  treatment: [{ required: true, message: '请输入处理方案', trigger: 'blur' }]
}

// 科室选项
const departments = [
  { label: '内科', value: 'internal' },
  { label: '外科', value: 'surgery' },
  { label: '儿科', value: 'pediatrics' },
  { label: '妇产科', value: 'obstetrics' },
  { label: '眼科', value: 'ophthalmology' },
  { label: '耳鼻喉科', value: 'ent' },
  { label: '口腔科', value: 'dental' },
  { label: '皮肤科', value: 'dermatology' },
  { label: '精神科', value: 'psychiatry' },
  { label: '中医科', value: 'tcm' }
]

// 获取记录详情
const fetchRecordDetail = async (id: string) => {
  loading.value = true
  try {
    const response = await recordsApi.getMedicalRecord(parseInt(id))
    if (response) {
      form.value = {
        ...form.value,
        visitDate: response.visit_date,
        hospital: response.hospital,
        department: response.department,
        doctor: response.doctor_name || '',
        chiefComplaint: response.reason,
        diagnosis: response.diagnosis || '',
        treatment: response.treatment || '',
        followUpDate: response.follow_up_date || '',
        cost: response.cost || 0,
        notes: response.notes || '',
        attachments: response.attachments?.map((item: any) => ({
          name: item.name,
          url: item.url
        })) || []
      }
    } else {
      ElMessage.error('获取记录详情失败')
    }
  } catch (error) {
    console.error('获取记录详情失败:', error)
    ElMessage.error('获取记录详情失败')
  } finally {
    loading.value = false
  }
}

// 处理表单提交
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      // 格式化数据以符合API要求
      const apiData = {
        visit_date: form.value.visitDate,
        hospital: form.value.hospital,
        department: form.value.department,
        doctor_name: form.value.doctor,
        reason: form.value.chiefComplaint,
        diagnosis: form.value.diagnosis,
        treatment: form.value.treatment,
        follow_up_date: form.value.followUpDate,
        cost: form.value.cost,
        notes: form.value.notes
      }
      
      let response
      if (isEdit.value) {
        response = await recordsApi.updateMedicalRecord(parseInt(route.params.id as string), apiData)
      } else {
        response = await recordsApi.createMedicalRecord(apiData)
      }
      
      if (response) {
        ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
        router.back()
      } else {
        ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
      }
    } catch (error) {
      console.error(isEdit.value ? '更新失败:' : '创建失败:', error)
      ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
    } finally {
      submitting.value = false
    }
  })
}

// 处理文件上传成功
const handleUploadSuccess = (response: any, file: UploadFile) => {
  if (response.success) {
    ElMessage.success('上传成功')
  } else {
    ElMessage.error(response.message || '上传失败')
  }
}

// 处理文件上传失败
const handleUploadError = () => {
  ElMessage.error('上传失败')
}

// 处理文件移除
const handleRemove = (file: UploadFile) => {
  const index = form.value.attachments.indexOf(file)
  if (index !== -1) {
    form.value.attachments.splice(index, 1)
  }
}

// 初始化
onMounted(async () => {
  const id = route.params.id
  if (id) {
    isEdit.value = true
    await fetchRecordDetail(id as string)
  }
})
</script>

<style scoped>
.medical-record-form {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 500;
}

.form-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.attachment-upload {
  width: 100%;
}

.form-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 32px;
}

@media screen and (max-width: 768px) {
  .medical-record-form {
    padding: 10px;
  }

  .page-header h2 {
    font-size: 20px;
  }

  :deep(.el-form-item__label) {
    width: 80px !important;
  }
}
</style> 
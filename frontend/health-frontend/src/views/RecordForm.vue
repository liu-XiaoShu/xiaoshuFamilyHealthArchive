<template>
  <div class="record-form-container">
    <el-card>
      <template #header>
        <div class="form-header">
          <h2>{{ isEdit ? '编辑记录' : '新建记录' }}</h2>
          <el-button @click="$router.back()">返回</el-button>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        v-loading="loading"
        @submit.prevent="handleSubmit"
      >
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入记录标题" />
        </el-form-item>

        <el-form-item label="记录类型" prop="record_type">
          <el-select v-model="form.record_type" placeholder="请选择记录类型" style="width: 100%">
            <el-option label="体检报告" value="physical_exam" />
            <el-option label="就医记录" value="medical_visit" />
            <el-option label="用药记录" value="medication" />
            <el-option label="疾病史" value="disease_history" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>

        <el-form-item label="记录日期" prop="date">
          <el-date-picker
            v-model="form.date"
            type="date"
            placeholder="请选择日期"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            rows="4"
            placeholder="请输入详细描述"
          />
        </el-form-item>

        <el-form-item label="附件">
          <el-upload
            action="/api/upload"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :before-upload="beforeUpload"
            multiple
          >
            <el-button type="primary">点击上传</el-button>
            <template #tip>
              <div class="el-upload__tip">
                支持jpg、jpeg、png、pdf格式，单个文件不超过10MB
              </div>
            </template>
          </el-upload>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            native-type="submit"
            :loading="recordsStore.loading"
            class="submit-btn"
          >
            {{ isEdit ? '保存修改' : '创建记录' }}
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { FormInstance } from 'element-plus'
import { useRecordsStore } from '@/stores/records'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()
const recordsStore = useRecordsStore()
const formRef = ref<FormInstance>()
const loading = ref(false)

const isEdit = computed(() => !!route.params.id)

const form = reactive({
  title: '',
  record_type: '',
  date: '',
  description: '',
  attachments: [] as string[]
})

const rules = {
  title: [
    { required: true, message: '请输入标题', trigger: 'blur' },
    { min: 2, max: 100, message: '标题长度在2-100个字符之间', trigger: 'blur' }
  ],
  record_type: [
    { required: true, message: '请选择记录类型', trigger: 'change' }
  ],
  date: [
    { required: true, message: '请选择日期', trigger: 'change' }
  ],
  description: [
    { required: true, message: '请输入描述', trigger: 'blur' },
    { min: 10, message: '描述至少10个字符', trigger: 'blur' }
  ]
}

// 如果是编辑模式，获取记录详情
onMounted(async () => {
  if (isEdit.value) {
    try {
      loading.value = true
      const record = await recordsStore.getRecordDetail(Number(route.params.id))
      Object.assign(form, {
        ...record,
        date: dayjs(record.date).format('YYYY-MM-DD')
      })
    } catch (error: any) {
      ElMessage.error(error || '获取记录详情失败')
      router.push('/records')
    } finally {
      loading.value = false
    }
  }
})

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    if (isEdit.value) {
      await recordsStore.updateRecord(Number(route.params.id), form)
      ElMessage.success('更新成功')
    } else {
      await recordsStore.createRecord(form)
      ElMessage.success('创建成功')
    }
    router.push('/records')
  } catch (error: any) {
    ElMessage.error(error || (isEdit.value ? '更新失败' : '创建失败'))
  }
}

const beforeUpload = (file: File) => {
  const isValidType = ['image/jpeg', 'image/png', 'application/pdf'].includes(file.type)
  const isLt10M = file.size / 1024 / 1024 < 10

  if (!isValidType) {
    ElMessage.error('只能上传jpg、jpeg、png、pdf格式的文件')
    return false
  }
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过10MB')
    return false
  }
  return true
}

const handleUploadSuccess = (response: any) => {
  form.attachments.push(response.url)
  ElMessage.success('上传成功')
}

const handleUploadError = () => {
  ElMessage.error('上传失败')
}
</script>

<style scoped>
.record-form-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-header h2 {
  margin: 0;
}

.submit-btn {
  width: 100%;
}

.el-upload__tip {
  color: #909399;
  font-size: 12px;
  margin-top: 8px;
}
</style> 
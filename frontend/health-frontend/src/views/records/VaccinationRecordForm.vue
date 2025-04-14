<template>
  <div class="vaccination-record-form">
    <div class="page-header">
      <h2>{{ isEdit ? '编辑疫苗接种记录' : '新建疫苗接种记录' }}</h2>
    </div>

    <el-card v-loading="loading">
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-position="top"
        @submit.prevent="handleSubmit"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="疫苗名称" prop="vaccine_name">
              <el-input
                v-model="formData.vaccine_name"
                placeholder="请输入疫苗名称"
                maxlength="100"
                show-word-limit
              />
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item label="接种地点" prop="location">
              <el-input
                v-model="formData.location"
                placeholder="请输入接种地点"
                maxlength="200"
                show-word-limit
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="接种日期" prop="vaccination_date">
              <el-date-picker
                v-model="formData.vaccination_date"
                type="date"
                placeholder="请选择接种日期"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item label="下次接种日期" prop="next_due_date">
              <el-date-picker
                v-model="formData.next_due_date"
                type="date"
                placeholder="请选择下次接种日期（可选）"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="备注" prop="notes">
          <el-input
            v-model="formData.notes"
            type="textarea"
            :rows="4"
            placeholder="请输入备注信息"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <div class="form-actions">
          <el-button @click="$router.back()">取消</el-button>
          <el-button type="primary" native-type="submit" :loading="submitting">
            保存
          </el-button>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useRecordsStore } from '@/stores/records'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'

const route = useRoute()
const router = useRouter()
const recordsStore = useRecordsStore()
const authStore = useAuthStore()

const formRef = ref<FormInstance>()
const loading = ref(false)
const submitting = ref(false)

const isEdit = computed(() => !!route.params.id)
const recordId = computed(() => Number(route.params.id))

const formData = reactive({
  vaccine_name: '',
  vaccination_date: '',
  next_due_date: '',
  location: '',
  notes: '',
  user: authStore.user?.id
})

const rules = {
  vaccine_name: [
    { required: true, message: '请输入疫苗名称', trigger: 'blur' },
    { max: 100, message: '疫苗名称不能超过100个字符', trigger: 'blur' }
  ],
  location: [
    { required: true, message: '请输入接种地点', trigger: 'blur' },
    { max: 200, message: '接种地点不能超过200个字符', trigger: 'blur' }
  ],
  vaccination_date: [
    { required: true, message: '请选择接种日期', trigger: 'change' }
  ]
}

const fetchRecord = async () => {
  if (!isEdit.value) return
  
  loading.value = true
  try {
    const record = recordsStore.getVaccinationRecordById(recordId.value)
    if (record) {
      Object.assign(formData, record)
    }
  } catch (error) {
    ElMessage.error('获取记录失败')
    router.push('/records/vaccination')
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    submitting.value = true
    
    if (isEdit.value) {
      await recordsStore.updateVaccinationRecord(recordId.value, formData)
      ElMessage.success('更新成功')
    } else {
      await recordsStore.createVaccinationRecord(formData)
      ElMessage.success('创建成功')
    }
    
    router.push('/records/vaccination')
  } catch (error: any) {
    if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail)
    } else {
      ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
    }
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchRecord()
})
</script>

<style scoped>
.vaccination-record-form {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
}

.form-actions {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style> 